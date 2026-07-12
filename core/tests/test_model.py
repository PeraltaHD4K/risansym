import pytest
from risansym.model import Model
from risansym.event import Event

class DummyModel(Model):
    def init(self):
        pass
    
    def receive(self, event: Event):
        pass

def test_model_unbound_transmit():
    model = DummyModel()
    with pytest.raises(RuntimeError, match="not bound to a Process"):
        model.transmit(Event(time=1.0, source=1, target=2, name="MSG", payload={}))

def test_model_unbound_log():
    model = DummyModel()
    with pytest.raises(RuntimeError, match="not bound to a Process"):
        model.log("test")

def test_model_repr():
    model = DummyModel()
    assert repr(model) == "<DummyModel(node_id=0, clock=0.0)>"

def test_model_repr_bound():
    """__repr__ should show updated node_id when bound."""
    class MockSink:
        def transmit(self, event): pass
        def log(self, message): pass
        
    model = DummyModel()
    model.set_sink(MockSink(), [2, 3], 1)
    assert repr(model) == "<DummyModel(node_id=1, clock=0.0)>"
