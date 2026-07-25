import pytest

from risansym.process import Process
from risansym.model import Model
from risansym.event import Event
from risansym.exceptions import InvalidEventError
from risansym.results import ScheduleResult
from risansym.simulator import Simulator
from risansym.engine.runtime import SimulationRuntime


def runtime() -> SimulationRuntime:
    return SimulationRuntime(Simulator(10.0))


class DummyModel(Model):
    def init(self):
        pass

    def receive(self, event: Event):
        self.log(f"Received {event.name}")


def test_process_binding():
    sim = runtime()
    process = Process([2, 3], sim, 1)

    assert repr(process) == "<Process(node_id=1, neighbors=[2, 3])>"

    model = DummyModel()
    process._bind_model(model)

    assert process.model is model
    assert model.node_id == 1
    assert model.neighbors == [2, 3]


def test_process_receive():
    sim = runtime()
    process = Process([2], sim, 1)
    model = DummyModel()
    process._bind_model(model)

    event = Event(time=1.0, source=2, target=1, name="TEST", payload={})
    process.receive(event)


def test_process_transmit_and_log():
    sim = runtime()
    process = Process([2], sim, 1)
    model = DummyModel()
    process._bind_model(model)

    event = Event(time=1.0, source=1, target=2, name="TEST", payload={})
    result = process.transmit(event)

    assert sim.is_on
    assert sim.pending_events == 1
    assert result is ScheduleResult.SCHEDULED

    process.log("Test log")


def test_process_rejects_spoofed_source():
    process = Process([2], runtime(), 1)

    with pytest.raises(InvalidEventError, match="source 2"):
        process.transmit(Event(time=1.0, source=2, target=2, name="TEST"))


def test_process_rejects_non_neighbor_target():
    process = Process([2], runtime(), 1)

    with pytest.raises(InvalidEventError, match="not a neighbor"):
        process.transmit(Event(time=1.0, source=1, target=3, name="TEST"))


def test_process_allows_self_messages():
    process = Process([2], runtime(), 1)

    assert (
        process.transmit(Event(time=1.0, source=1, target=1, name="TIMEOUT"))
        is ScheduleResult.SCHEDULED
    )
