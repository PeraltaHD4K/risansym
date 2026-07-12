from risansym.process import Process
from risansym.model import Model
from risansym.event import Event
from risansym.simulator import Simulator

class DummyModel(Model):
    def init(self):
        pass
    def receive(self, event: Event):
        self.log(f"Received {event.name}")

def test_process_binding():
    sim = Simulator(10.0)
    process = Process([2, 3], sim, 1)
    
    assert repr(process) == "<Process(node_id=1, neighbors=[2, 3])>"
    
    model = DummyModel()
    process.set_model(model)
    
    assert process.model is model
    assert model.node_id == 1
    assert model.neighbors == [2, 3]

def test_process_receive():
    sim = Simulator(10.0)
    process = Process([2], sim, 1)
    model = DummyModel()
    process.set_model(model)
    
    event = Event(time=1.0, source=2, target=1, name="TEST", payload={})
    process.receive(event)
    
def test_process_transmit_and_log():
    sim = Simulator(10.0)
    process = Process([2], sim, 1)
    model = DummyModel()
    process.set_model(model)
    
    event = Event(time=1.0, source=1, target=2, name="TEST", payload={})
    process.transmit(event)
    
    assert sim.is_on
    assert len(sim._agenda) == 1
    
    process.log("Test log")
