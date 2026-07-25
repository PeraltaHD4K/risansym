"""Incremental execution, limits, and result semantics."""

import pytest

from risansym.event import Event
from risansym.exceptions import ConfigurationError, SimulationLimitReached
from risansym.model import Model
from risansym.results import SimulationState, TerminationReason
from risansym.simulation import Simulation


class PassiveModel(Model):
    def init(self) -> None:
        pass

    def receive(self, event: Event) -> None:
        pass


class StopModel(PassiveModel):
    def __init__(self, simulation: Simulation) -> None:
        super().__init__()
        self.simulation = simulation

    def receive(self, event: Event) -> None:
        self.simulation.request_stop()


class RecordingModel(PassiveModel):
    def __init__(self, names: list[str]) -> None:
        super().__init__()
        self.names = names

    def receive(self, event: Event) -> None:
        self.names.append(event.name)


def prepared_simulation(*times: float, maxtime: float = 20.0) -> Simulation:
    simulation = Simulation([[]], maxtime, app_logs=False)
    simulation.set_model(PassiveModel(), 1)
    simulation.initialize_all()
    for index, event_time in enumerate(times):
        simulation.seed_event(
            Event(
                time=event_time,
                source=1,
                target=1,
                name=f"EVENT_{index}",
            )
        )
    return simulation


def test_step_processes_exactly_one_event_and_can_continue() -> None:
    simulation = prepared_simulation(1.0, 2.0)

    first = simulation.step()
    assert first.processed_events == 1
    assert first.pending_events == 1
    assert first.reason is TerminationReason.MAX_EVENTS
    assert first.state is SimulationState.STOPPED

    final = simulation.run()
    assert final.processed_events == 2
    assert final.pending_events == 0
    assert final.complete


def test_run_budget_returns_incomplete_result() -> None:
    simulation = prepared_simulation(1.0, 2.0, 3.0)

    partial = simulation.run(max_events=2)
    assert partial.reason is TerminationReason.MAX_EVENTS
    assert not partial.complete
    assert partial.pending_events == 1

    assert simulation.run().complete


def test_continuation_preserves_fifo_order_and_cumulative_metrics() -> None:
    names: list[str] = []
    simulation = Simulation([[]], 10.0)
    simulation.set_model(RecordingModel(names), 1)
    simulation.initialize_all()
    for name in ("FIRST", "SECOND", "THIRD"):
        simulation.seed_event(Event(time=1.0, source=1, target=1, name=name))

    first = simulation.run(max_events=1)
    final = simulation.run()

    assert names == ["FIRST", "SECOND", "THIRD"]
    assert first.processed_events == 1
    assert final.processed_events == 3
    assert final.scheduled_events == 3


def test_run_until_preserves_future_events() -> None:
    simulation = prepared_simulation(1.0, 5.0)

    partial = simulation.run_until(2.0)
    assert partial.reason is TerminationReason.TIME_LIMIT
    assert partial.simulated_time == 1.0
    assert partial.pending_events == 1

    final = simulation.run_until(5.0)
    assert final.complete
    assert final.processed_events == 2


def test_cooperative_stop_can_continue() -> None:
    simulation = Simulation([[]], 10.0)
    simulation.set_model(StopModel(simulation), 1)
    simulation.initialize_all()
    simulation.seed_event(Event(time=1.0, source=1, target=1, name="STOP"))
    simulation.seed_event(Event(time=2.0, source=1, target=1, name="LATER"))

    partial = simulation.run()
    assert partial.reason is TerminationReason.STOP_REQUESTED
    assert partial.processed_events == 1
    assert partial.pending_events == 1

    assert simulation.run().complete


def test_time_horizon_is_reported() -> None:
    simulation = prepared_simulation(maxtime=5.0)
    simulation.seed_event(Event(time=6.0, source=1, target=1, name="TOO_LATE"))

    result = simulation.run()
    assert result.reason is TerminationReason.MAX_TIME
    assert result.dropped_by_time_horizon == 1


@pytest.mark.parametrize("budget", [0, -1, True, 1.5])
def test_invalid_event_budget_is_rejected(budget: object) -> None:
    with pytest.raises(ConfigurationError, match="positive integer"):
        Simulation([[]], 10.0, max_events=budget)  # type: ignore[arg-type]


def test_agenda_limit_is_enforced() -> None:
    simulation = Simulation([[]], 10.0, max_agenda_size=1)
    simulation.initialize_all()
    simulation.seed_event(Event(time=1.0, source=1, target=1, name="FIRST"))

    with pytest.raises(SimulationLimitReached, match="Agenda limit"):
        simulation.seed_event(Event(time=2.0, source=1, target=1, name="SECOND"))
