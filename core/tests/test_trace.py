"""Tests for trace output generation (end-to-end with file I/O)."""

import json
import pytest
from risansym.simulation import Simulation
from risansym.model import Model
from risansym.event import Event
from risansym.exceptions import ConfigurationError
from risansym.schemas import AppLogEvent, TraceCapture, TraceMetadata, TraceOutput
from risansym.trace import TraceCollector


class EchoModel(Model):
    """Simple model that echoes one message back and forth."""

    def init(self):
        self.transmit(
            Event(
                time=self.clock + 1.0,
                source=self.node_id,
                target=self.neighbors[0],
                name="ECHO",
                payload={"step": 0},
            )
        )

    def receive(self, event):
        step = event.payload.get("step", 0)
        if step < 2:
            self.transmit(
                Event(
                    time=self.clock + 1.0,
                    source=self.node_id,
                    target=event.source,
                    name="ECHO",
                    payload={"step": step + 1},
                )
            )

    def get_state(self):
        return {"clock": self.clock}


@pytest.fixture
def two_node_sim(tmp_path):
    """Create a 2-node simulation with trace enabled."""
    topo = tmp_path / "topo.txt"
    topo.write_text("2\n1\n")
    trace_path = tmp_path / "output.json"

    sim = Simulation.from_file(
        filename=topo,
        maxtime=20.0,
        algo_name="EchoTest",
        trace_network=False,
        app_logs=False,
        trace_enabled=True,
        trace_path=str(trace_path),
    )
    sim.set_model(EchoModel(), node_id=1)
    sim.set_model(EchoModel(), node_id=2)
    sim.initialize_all()
    return sim, trace_path


class TestTraceGeneration:
    def test_trace_file_is_created(self, two_node_sim):
        sim, trace_path = two_node_sim
        sim.run()
        assert trace_path.exists()

    def test_trace_is_valid_json(self, two_node_sim):
        sim, trace_path = two_node_sim
        sim.run()
        data = json.loads(trace_path.read_text())
        assert "metadata" in data
        assert "trace" in data

    def test_trace_validates_against_schema(self, two_node_sim):
        sim, trace_path = two_node_sim
        sim.run()
        output = TraceOutput.model_validate_json(trace_path.read_text())
        assert output.metadata.algorithm == "EchoTest"
        assert len(output.trace) > 0

    def test_trace_contains_transmit_and_receive_events(self, two_node_sim):
        sim, trace_path = two_node_sim
        sim.run()
        output = TraceOutput.model_validate_json(trace_path.read_text())
        actions = {e.action for e in output.trace}
        assert "TRANSMIT" in actions
        assert "RECEIVE" in actions

    def test_trace_captures_node_state(self, two_node_sim):
        sim, trace_path = two_node_sim
        sim.run()
        output = TraceOutput.model_validate_json(trace_path.read_text())
        # At least some events should have node_state captured
        events_with_state = [
            e for e in output.trace if hasattr(e, "node_state") and e.node_state is not None
        ]
        assert len(events_with_state) > 0

    def test_execution_result_populated(self, two_node_sim):
        sim, _ = two_node_sim
        result = sim.run()
        assert result.simulated_time > 0
        assert result.processed_events > 0
        assert result.execution_real_time_seconds >= 0

    def test_trace_collector_cap(self):
        # T8: TraceCollector memory limit
        collector = TraceCollector(max_events=5)

        # Insert 5 events, no warning
        for i in range(5):
            collector.record(AppLogEvent(clock=float(i), source=1, message="test"))

        assert len(collector) == 5

        # 6th event should trigger warning and pop first
        with pytest.warns(ResourceWarning, match="has reached its limit of 5 events"):
            collector.record(AppLogEvent(clock=5.0, source=1, message="test"))

        assert len(collector) == 5
        # First event was at clock=0.0, now it's gone
        assert collector._trace[0].clock == 1.0
        assert collector.total_events == 6
        assert collector.dropped_events == 1

    @pytest.mark.parametrize("limit", [0, -1, 1_000_001, None, True])
    def test_trace_collector_rejects_invalid_cap(self, limit):
        with pytest.raises(ConfigurationError, match="max_events"):
            TraceCollector(max_events=limit)

    def test_truncated_trace_is_identified_in_metadata(self, tmp_path):
        trace_path = tmp_path / "truncated.json"
        sim = Simulation(
            [[]],
            10.0,
            trace_enabled=True,
            trace_path=trace_path,
            trace_max_events=1,
        )
        sim.initialize_all()
        sim.seed_event(Event(time=0.0, source=1, target=1, name="ONE"))
        with pytest.warns(ResourceWarning):
            sim.seed_event(Event(time=1.0, source=1, target=1, name="TWO"))
        with pytest.warns(UserWarning, match="no model bound"):
            sim.run()

        output = TraceOutput.model_validate_json(trace_path.read_text())
        assert output.metadata.capture.truncated is True
        assert output.metadata.capture.recorded_events == 1
        assert output.metadata.capture.dropped_events > 0

    def test_atomic_dump_preserves_existing_file_and_cleans_temporary_file(
        self, tmp_path, monkeypatch
    ):
        target = tmp_path / "trace.json"
        target.write_text("existing", encoding="utf-8")
        collector = TraceCollector(max_events=10)
        collector.record(AppLogEvent(clock=0.0, source=1, message="test"))
        metadata = TraceMetadata(
            algorithm="Test",
            topology="single",
            execution_date="2026-07-25T00:00:00Z",
            parameters={},
            metrics={},
            capture=TraceCapture(
                max_events=10,
                recorded_events=1,
                dropped_events=0,
                truncated=False,
            ),
        )

        def fail_replace(self, target_path):
            raise OSError("simulated atomic replacement failure")

        monkeypatch.setattr(type(target), "replace", fail_replace)

        with pytest.raises(OSError, match="replacement failure"):
            collector.dump(target, metadata)

        assert target.read_text(encoding="utf-8") == "existing"
        assert list(tmp_path.glob("*.tmp")) == []
