import pytest

from risansym.event import Event
from risansym.exceptions import CausalityError, InvalidEventError
from risansym.plugins.base import SimulationPlugin
from risansym.results import ScheduleResult
from risansym.simulator import Simulator


def test_event_ordering():
    engine = Simulator(maxtime=10.0)

    # Insert events out of order
    engine.insert_event(Event(time=3.0, source=1, target=2, name="MSG_3", payload={}))
    engine.insert_event(Event(time=1.0, source=1, target=2, name="MSG_1", payload={}))
    engine.insert_event(Event(time=2.0, source=1, target=2, name="MSG_2", payload={}))

    # Pop should return them in time order
    e1 = engine.pop_event()
    assert e1.time == 1.0
    assert e1.name == "MSG_1"

    e2 = engine.pop_event()
    assert e2.time == 2.0

    e3 = engine.pop_event()
    assert e3.time == 3.0

    # Engine should be off when empty
    assert engine.is_on is False


def test_event_tie_breaking():
    """Test that events scheduled at the exact same time are popped in FIFO order (REL-02)."""
    engine = Simulator(maxtime=10.0)

    # Insert multiple events at time 5.0
    engine.insert_event(Event(time=5.0, source=1, target=2, name="FIRST", payload={}))
    engine.insert_event(Event(time=5.0, source=1, target=2, name="SECOND", payload={}))
    engine.insert_event(Event(time=5.0, source=1, target=2, name="THIRD", payload={}))

    # Pop should return them in insertion order
    e1 = engine.pop_event()
    assert e1.name == "FIRST"

    e2 = engine.pop_event()
    assert e2.name == "SECOND"

    e3 = engine.pop_event()
    assert e3.name == "THIRD"


def test_maxtime_limit():
    engine = Simulator(maxtime=5.0)
    engine.insert_event(Event(time=1.0, source=1, target=2, name="MSG_1", payload={}))
    result = engine.insert_event(Event(time=6.0, source=1, target=2, name="MSG_6", payload={}))

    # 1.0 is valid
    assert engine.is_on is True
    engine.pop_event()

    # 6.0 exceeds maxtime, so is_on should be False
    assert engine.is_on is False
    assert result is ScheduleResult.DROPPED_TIME_HORIZON
    assert engine.dropped_by_time_horizon == 1


class TransformingPlugin(SimulationPlugin):
    def __init__(self, transformed: object) -> None:
        self.transformed = transformed

    def on_event_schedule(self, event, simulator, node_state=None):
        return self.transformed


def test_plugin_cannot_move_event_into_the_past() -> None:
    engine = Simulator(maxtime=10.0)
    engine.clock = 5.0
    engine.plugin_manager.attach(
        TransformingPlugin(Event(time=1.0, source=1, target=1, name="PAST"))
    )

    with pytest.raises(CausalityError, match="clock is at"):
        engine.insert_event(Event(time=5.0, source=1, target=1, name="VALID"))


def test_plugin_cannot_bypass_time_horizon() -> None:
    engine = Simulator(maxtime=10.0)
    engine.plugin_manager.attach(
        TransformingPlugin(Event(time=20.0, source=1, target=1, name="FUTURE"))
    )

    result = engine.insert_event(Event(time=1.0, source=1, target=1, name="VALID"))

    assert result is ScheduleResult.DROPPED_TIME_HORIZON
    assert engine.is_on is False
    assert engine.dropped_by_time_horizon == 1


def test_plugin_can_explicitly_drop_an_event() -> None:
    engine = Simulator(maxtime=10.0)
    engine.plugin_manager.attach(TransformingPlugin(None))

    result = engine.insert_event(Event(time=1.0, source=1, target=1, name="VALID"))

    assert result is ScheduleResult.DROPPED_BY_PLUGIN
    assert engine.is_on is False
    assert engine.dropped_by_plugins == 1


def test_plugin_must_return_event_or_none() -> None:
    engine = Simulator(maxtime=10.0)
    engine.plugin_manager.attach(TransformingPlugin("not-an-event"))

    with pytest.raises(InvalidEventError, match="Event or None"):
        engine.insert_event(Event(time=1.0, source=1, target=1, name="VALID"))
