"""Simulation lifecycle and transactional initialization tests."""

from pathlib import Path

import pytest

from risansym.event import Event
from risansym.exceptions import SimulationError
from risansym.model import Model
from risansym.plugins.tracer import JSONTracerPlugin
from risansym.results import SimulationState
from risansym.simulation import Simulation


class PassiveModel(Model):
    def init(self) -> None:
        pass

    def receive(self, event: Event) -> None:
        pass


class SchedulingModel(PassiveModel):
    def init(self) -> None:
        self.transmit(
            Event(
                time=1.0,
                source=self.node_id,
                target=self.node_id,
                name="INITIAL",
            )
        )


class FailingInitModel(PassiveModel):
    def init(self) -> None:
        raise ValueError("broken init")


def test_lifecycle_reaches_completed_state() -> None:
    simulation = Simulation([[]], 10.0)
    simulation.set_model(PassiveModel(), 1)
    assert simulation.state is SimulationState.CREATED

    simulation.initialize_all()
    assert simulation.state is SimulationState.READY

    result = simulation.run()
    assert result.complete
    assert simulation.state is SimulationState.COMPLETED


def test_initialization_failure_is_transactional_and_identifies_node() -> None:
    simulation = Simulation([[2], [1]], 10.0)
    simulation.set_model(SchedulingModel(), 1)
    simulation.set_model(FailingInitModel(), 2)

    with pytest.raises(SimulationError, match="node 2") as captured:
        simulation.initialize_all()

    assert isinstance(captured.value.__cause__, ValueError)
    assert simulation.state is SimulationState.FAILED
    assert simulation.engine.pending_events == 0
    assert simulation.engine.scheduled_events == 0


@pytest.mark.parametrize("operation", ["set_model", "attach", "initialize"])
def test_configuration_is_frozen_after_initialization(operation: str) -> None:
    simulation = Simulation([[]], 10.0)
    simulation.set_model(PassiveModel(), 1)
    simulation.initialize_all()

    with pytest.raises(SimulationError, match="not valid"):
        if operation == "set_model":
            simulation.set_model(PassiveModel(), 1)
        elif operation == "attach":
            simulation.attach(JSONTracerPlugin())
        else:
            simulation.initialize_all()


def test_completed_simulation_cannot_run_again() -> None:
    simulation = Simulation([[]], 10.0)
    simulation.initialize_all()
    simulation.run()

    with pytest.raises(SimulationError, match="completed"):
        simulation.run()


def test_context_manager_protocol_was_removed() -> None:
    simulation = Simulation([[]], 10.0)
    assert not hasattr(simulation, "__enter__")
    assert not hasattr(simulation, "__exit__")


def test_tracer_is_accessible_without_private_engine_state(tmp_path: Path) -> None:
    trace_path = tmp_path / "trace.json"
    simulation = Simulation([[]], 10.0)
    tracer = JSONTracerPlugin(trace_path=trace_path)
    simulation.attach(tracer)
    simulation.initialize_all()
    simulation.run()

    assert tracer in simulation.plugins
    assert tracer.exported_path == trace_path
    assert trace_path.exists()
