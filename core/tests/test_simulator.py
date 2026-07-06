from risansym.event import Event
from risansym.simulator import Simulator

def test_event_ordering():
    engine = Simulator(maxtime=10.0, debug=False)
    
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

def test_maxtime_limit():
    engine = Simulator(maxtime=5.0, debug=False)
    engine.insert_event(Event(time=1.0, source=1, target=2, name="MSG_1", payload={}))
    engine.insert_event(Event(time=6.0, source=1, target=2, name="MSG_6", payload={}))
    
    # 1.0 is valid
    assert engine.is_on is True
    engine.pop_event()
    
    # 6.0 exceeds maxtime, so is_on should be False
    assert engine.is_on is False
