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


def test_basic_simulation(temp_topology):
    sim = Simulation.from_file(filename=temp_topology, maxtime=10.0, algo_name="PingPong", trace_network=False, app_logs=False, trace_enabled=False)
    
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
    
    tracer = next((p for p in sim.engine._plugins if type(p).__name__ == "JSONTracerPlugin"), None)
    assert tracer is not None
