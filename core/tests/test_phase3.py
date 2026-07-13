import pytest
from risansym.simulation import Simulation
from risansym.model import Model
from risansym.process import Process
from risansym.event import Event
from risansym.simulator import Simulator

@pytest.fixture
def temp_topology(tmp_path) -> str:
    topo_file = tmp_path / "test_topo.txt"
    topo_file.write_text("2\n1\n")
    return str(topo_file)

class DummyModel(Model):
    def init(self) -> None:
        self.log("init")
        
    def receive(self, event: Event) -> None:
        if event.name == "REENTRANT":
            # 7. Transmit re-entrante desde dentro de receive()
            self.transmit(Event(time=self.clock + 1.0, source=self.node_id, target=self.node_id, name="NESTED", payload={}))
        self.log("received")

class StateModel(Model):
    def init(self) -> None:
        self.transmit(Event(time=1.0, source=self.node_id, target=self.node_id, name="TEST", payload={}))
    def receive(self, event: Event) -> None:
        pass
    def get_state(self) -> dict[str, str]:
        # 9. Override de Model.get_state()
        return {"custom_key": "custom_value"}

def test_simulation_no_models(temp_topology) -> None:
    # 1. Simulación sin modelos asignados
    sim = Simulation(temp_topology, 10.0, "NoModelsAlgo", trace_enabled=False)
    # Simulator should just do nothing, wait, Simulator.__init__ maxtime > 0, we run maxtime=10
    sim.run()
    assert sim.engine.clock == 0.0  # Nothing happened

def test_simulation_partial_models(temp_topology) -> None:
    # 2. Simulación con modelos parciales
    sim = Simulation(temp_topology, 10.0, "PartialAlgo", trace_enabled=False)
    sim.set_model(DummyModel(), 1)
    sim.run()
    # Should not crash, just ignore unassigned nodes

def test_negative_time_event() -> None:
    # 3. Evento con tiempo negativo
    # Although Event allows negative time, the simulator agenda doesn't care, 
    # but let's test that it can be created and sorted.
    e1 = Event(time=-1.0, source=1, target=2, name="NEG", payload={})
    e2 = Event(time=0.0, source=1, target=2, name="ZERO", payload={})
    assert e1 < e2

def test_pop_empty_agenda() -> None:
    # 4. pop_event() con agenda vacía
    engine = Simulator(maxtime=10.0)
    with pytest.raises(RuntimeError, match="Cannot pop from an empty event agenda"):
        engine.pop_event()

def test_process_transmit_no_model() -> None:
    # 5. Process.transmit() sin modelo asignado
    engine = Simulator(maxtime=10.0)
    proc = Process([2], engine, 1)
    # Should not crash, just logs a warning
    proc.transmit(Event(time=1.0, source=1, target=2, name="TEST", payload={}))
    assert engine.is_on

def test_large_scale(temp_topology) -> None:
    # 6. Test de estrés a gran escala
    sim = Simulation(temp_topology, 10.0, "Stress", trace_enabled=False)
    for i in range(1, len(sim.table)):
        sim.set_model(DummyModel(), i)
    sim.run()
    # Just checking it doesn't crash

def test_reentrant_transmit(temp_topology) -> None:
    # 7. Transmit re-entrante
    sim = Simulation(temp_topology, 10.0, "Reentrant", trace_enabled=False)
    model = DummyModel()
    sim.set_model(model, 1)
    sim.initialize_all()
    # Insert an event manually
    sim.engine.insert_event(Event(time=1.0, source=1, target=1, name="REENTRANT", payload={}))
    sim.run()
    # Should have processed NESTED

def test_app_log_e2e(temp_topology) -> None:
    # 8. Traza con eventos APP_LOG
    sim = Simulation(temp_topology, 10.0, "AppLog", trace_enabled=True)
    sim.set_model(DummyModel(), 1)
    sim.initialize_all()
    with sim:
        sim.run()
    assert sim.collector is not None
    logs = [e for e in sim.collector if getattr(e, "action", None) == "APP_LOG"]
    assert len(logs) > 0

def test_get_state_override(temp_topology) -> None:
    # 9. Override get_state()
    sim = Simulation(temp_topology, 10.0, "StateAlgo", trace_enabled=True)
    sim.set_model(StateModel(), 1)
    sim.initialize_all()
    with sim:
        sim.run()
    assert sim.collector is not None
    transmits = [e for e in sim.collector if getattr(e, "action", None) == "TRANSMIT"]
    assert len(transmits) > 0
    assert transmits[0].node_state == {"custom_key": "custom_value"}

def test_simulation_repr(temp_topology) -> None:
    # 10. Simulation.__repr__
    sim = Simulation(temp_topology, 10.0, "ReprAlgo", trace_enabled=False)
    rep = repr(sim)
    assert "Simulation" in rep
    assert "ReprAlgo" in rep
