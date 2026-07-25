"""Adversarial tests for resource limits, paths, and plugin failures."""

from pathlib import Path

from risansym.event import Event
from risansym.model import Model
from risansym.plugins.tracer import JSONTracerPlugin
from risansym.simulation import Simulation


class InfinitePingModel(Model):
    def init(self) -> None:
        pass

    def receive(self, event: Event) -> None:
        self.transmit(
            Event(
                time=self.clock,
                name="PING",
                source=self.node_id,
                target=event.source,
                payload={"storm": True},
            )
        )


def _two_node_topology(tmp_path: Path) -> Path:
    path = tmp_path / "topology.txt"
    path.write_text("2\n1\n", encoding="utf-8")
    return path


def test_event_storm_budget(tmp_path: Path) -> None:
    simulation = Simulation.from_file(
        _two_node_topology(tmp_path),
        100.0,
        max_events=50,
        app_logs=False,
    )
    simulation.set_model(InfinitePingModel(), 1)
    simulation.set_model(InfinitePingModel(), 2)
    simulation.initialize_all()
    simulation.seed_event(Event(time=0.0, name="START", source=1, target=1, payload={}))

    simulation.run()

    assert simulation.execution_metrics["total_messages"] == 50
    assert simulation.engine.is_on


def test_trace_path_components_are_confined_and_sanitized(tmp_path: Path) -> None:
    trace_directory = tmp_path / "traces"
    simulation = Simulation.from_file(
        _two_node_topology(tmp_path),
        10.0,
        algo_name="../Algorithm",
        app_logs=False,
    )
    simulation.attach(
        JSONTracerPlugin(
            trace_dir=str(trace_directory),
            trace_tag="../malicious",
        )
    )
    simulation.initialize_all()

    simulation.run()

    trace_files = list(trace_directory.rglob("*.json"))
    assert len(trace_files) == 1
    assert trace_files[0].resolve().is_relative_to(trace_directory.resolve())
    assert ".." not in trace_files[0].relative_to(trace_directory).parts


def test_non_critical_end_plugin_failure_is_isolated(tmp_path: Path) -> None:
    class EndFailingPlugin:
        requires_state_snapshot = False

        def on_start(self, simulation) -> None:
            pass

        def on_end(self, simulation) -> None:
            raise ValueError("Boom")

    simulation = Simulation.from_file(
        _two_node_topology(tmp_path),
        10.0,
        app_logs=False,
    )
    simulation.attach(EndFailingPlugin())
    simulation.initialize_all()

    simulation.run()

    assert simulation.execution_metrics["total_messages"] == 0
