"""Tests for trace output generation (end-to-end with file I/O)."""

import json
import pytest
from risansym.simulation import Simulation
from risansym.model import Model
from risansym.event import Event
from risansym.schemas import TraceOutput


class EchoModel(Model):
    """Simple model that echoes one message back and forth."""

    def init(self):
        self.transmit(Event(
            time=self.clock + 1.0,
            source=self.node_id,
            target=self.neighbors[0],
            name="ECHO",
            payload={"step": 0}
        ))

    def receive(self, event):
        step = event.payload.get("step", 0)
        if step < 2:
            self.transmit(Event(
                time=self.clock + 1.0,
                source=self.node_id,
                target=event.source,
                name="ECHO",
                payload={"step": step + 1}
            ))

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
        trace_network=False, app_logs=False,
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
        events_with_state = [e for e in output.trace if hasattr(e, "node_state") and e.node_state is not None]
        assert len(events_with_state) > 0

    def test_execution_metrics_populated(self, two_node_sim):
        sim, _ = two_node_sim
        sim.run()
        assert "simulated_time_elapsed" in sim.execution_metrics
        assert "total_messages" in sim.execution_metrics
        assert "execution_real_time_sec" in sim.execution_metrics
        assert sim.execution_metrics["total_messages"] > 0

    def test_trace_collector_cap(self):
        # T8: TraceCollector memory limit
        from risansym.trace import TraceCollector
        from risansym.schemas import AppLogEvent
        import pytest
        
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
