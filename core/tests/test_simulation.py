import pytest
from risansym.simulation import Simulation
from risansym.model import Model
from risansym.event import Event

class DummyModel(Model):
    def init(self):
        self.transmit(Event(time=self.clock + 1.0, source=self.id, target=self.neighbors[0], name="PING", payload={}))
        
    def receive(self, event):
        if event.name == "PING" and self.clock < 5.0:
            self.log(f"Received PING from {event.source}")
            self.transmit(Event(time=self.clock + 1.0, source=self.id, target=event.source, name="PONG", payload={}))
        elif event.name == "PONG" and self.clock < 5.0:
            self.transmit(Event(time=self.clock + 1.0, source=self.id, target=event.source, name="PING", payload={}))

@pytest.fixture
def temp_topology(tmp_path):
    topo_file = tmp_path / "topo.txt"
    # Adjacency list: Node 1 connects to 2, Node 2 connects to 1
    topo_file.write_text("2\n1\n")
    return topo_file

def test_basic_simulation(temp_topology):
    sim = Simulation.from_file(filename=temp_topology, maxtime=10.0, algo_name="PingPong", debug=False, trace=False)
    
    # Assign models
    sim.set_model(DummyModel(), node_id=1)
    sim.set_model(DummyModel(), node_id=2)
    
    # Initialize all processes
    sim.initialize_all()
    
    # Run simulation
    sim.run()
    
    # Verify metrics
    assert sim.execution_metrics["simulated_time_elapsed"] <= 10.0
    
    # The clock should advance to at least 5.0 because of the condition in receive
    assert sim.engine.clock >= 5.0
