import pytest
from risansym.simulation import Simulation
from risansym.model import Model
from risansym.event import Event

class DummyModel(Model):
    def init(self):
        self.transmit(Event(time=self.clock + 1.0, source=self.node_id, target=self.neighbors[0], name="PING", payload={}))
        
    def receive(self, event):
        if event.name == "PING" and self.clock < 5.0:
            self.log(f"Received PING from {event.source}")
            self.transmit(Event(time=self.clock + 1.0, source=self.node_id, target=event.source, name="PONG", payload={}))
        elif event.name == "PONG" and self.clock < 5.0:
            self.transmit(Event(time=self.clock + 1.0, source=self.node_id, target=event.source, name="PING", payload={}))

@pytest.fixture
def temp_topology(tmp_path):
    topo_file = tmp_path / "topo.txt"
    # Adjacency list: Node 1 connects to 2, Node 2 connects to 1
    topo_file.write_text("2\n1\n")
    return topo_file

def test_basic_simulation(temp_topology):
    sim = Simulation.from_file(filename=temp_topology, maxtime=10.0, algo_name="PingPong", debug=False, trace_enabled=False)
    
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

def test_simulation_deprecated_path_warning(temp_topology):
    with pytest.warns(DeprecationWarning, match="Passing a filename directly to Simulation"):
        sim = Simulation(temp_topology, maxtime=10.0)
    
    assert len(sim.graph) == 2

def test_simulation_trace_warning(temp_topology):
    # T5: Deprecated trace argument
    with pytest.warns(DeprecationWarning, match="The 'trace' argument is deprecated"):
        sim = Simulation(temp_topology, maxtime=10.0, trace=True)
    assert sim.trace_enabled is True

def test_simulation_double_save(temp_topology, monkeypatch):
    # T4: Prevent double trace save when using context manager
    sim = Simulation.from_file(temp_topology, maxtime=10.0, trace_enabled=True)
    
    save_calls = 0
    def mock_save_trace():
        nonlocal save_calls
        save_calls += 1
    
    monkeypatch.setattr(sim, "_save_trace", mock_save_trace)
    
    sim.initialize_all()
    with sim:
        sim.run()
        
    assert save_calls == 1
