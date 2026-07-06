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
    assert repr(model) == "<DummyModel(id=0, clock=0.0)>"
    
    # Mocking binding
    class MockSink:
        def transmit(self, event): pass
        def log(self, message): pass
        
    model.set_sink(MockSink(), [2, 3], 1)
    assert repr(model) == "<DummyModel(id=1, clock=0.0)>"
