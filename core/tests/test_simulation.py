from risansym.simulation import Simulation
from risansym.model import Model
from risansym.event import Event
from risansym.results import SimulationState


class DummyModel(Model):
    def init(self):
        self.transmit(
            Event(
                time=self.clock + 1.0,
                source=self.node_id,
                target=self.neighbors[0],
                name="PING",
                payload={},
            )
        )

    def receive(self, event):
        if event.name == "PING" and self.clock < 5.0:
            self.log(f"Received PING from {event.source}")
            self.transmit(
                Event(
                    time=self.clock + 1.0,
                    source=self.node_id,
                    target=event.source,
                    name="PONG",
                    payload={},
                )
            )
        elif event.name == "PONG" and self.clock < 5.0:
            self.transmit(
                Event(
                    time=self.clock + 1.0,
                    source=self.node_id,
                    target=event.source,
                    name="PING",
                    payload={},
                )
            )


def test_basic_simulation(temp_topology):
    sim = Simulation.from_file(
        filename=temp_topology,
        maxtime=10.0,
        algo_name="PingPong",
        trace_network=False,
        app_logs=False,
        trace_enabled=False,
    )

    # Assign models
    sim.set_model(DummyModel(), node_id=1)
    sim.set_model(DummyModel(), node_id=2)

    # Initialize all processes
    sim.initialize_all()

    # Run simulation
    result = sim.run()

    assert result.simulated_time <= 10.0
    assert result.state is SimulationState.COMPLETED

    # The clock should advance to at least 5.0 because of the condition in receive
    assert sim.engine.clock >= 5.0
