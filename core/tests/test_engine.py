import pytest
from risansym.event import Event
from risansym.exceptions import CausalityError, SimulationError
from risansym.simulator import Simulator
from risansym.engine.loop import EventLoop
from risansym.process import Process
from risansym.model import Model


class BadModel(Model):
    def init(self):
        pass

    def receive(self, event):
        raise ValueError("Intentional crash")


def test_causality_violation():
    sim = Simulator(maxtime=10.0)
    sim.clock = 2.0
    with pytest.raises(CausalityError, match="clock is at"):
        sim.insert_event(Event(time=1.5, source=1, target=2, name="PAST_EVENT", payload={}))


def test_event_loop_crash_resilience():
    sim = Simulator(maxtime=10.0)
    sim.insert_event(Event(time=1.0, source=1, target=1, name="A", payload={}))

    p = Process(node_id=1, neighbors=[2], engine=sim)
    p.set_model(BadModel())

    loop = EventLoop(simulator=sim, table=[None, p, None])

    with pytest.raises(
        SimulationError,
        match="Simulation crashed at node 1 while processing 'A'",
    ):
        loop.run(max_events=10)
