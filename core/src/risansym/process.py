from __future__ import annotations

from risansym.event import Event
from risansym.model import Model
from risansym.simulator import Simulator


class Process:
    """Entity that resides at a vertex of the topology graph.

    A process hosts exactly one :class:`Model` and mediates communication
    between the model's algorithm logic and the simulation engine.
    """

    def __init__(self, neighbors: list[int], engine: Simulator, node_id: int) -> None:
        self.neighbors = neighbors
        self.engine = engine
        self.id = node_id
        self.model: Model | None = None

    def __repr__(self) -> str:
        return f"<Process(id={self.id}, neighbors={self.neighbors})>"

    def set_model(self, model: Model) -> None:
        """Bind a model to this process without triggering initialization."""
        self.model = model
        self.model.set_sink(self, self.neighbors, self.id)

    def set_time(self, time: float) -> None:
        """Forward the simulation clock to the bound model."""
        if self.model:
            self.model.set_time(time)

    def transmit(self, event: Event) -> None:
        """Delegate event insertion to the engine, attaching the node's current state."""
        state = self.model.get_state() if self.model else None
        if state is None:
            import logging
            logging.getLogger(__name__).warning(
                "Process %d transmitted an event without a bound model.", self.id
            )
            state = {}
        self.engine.insert_event(event, node_state=state)

    def receive(self, event: Event) -> None:
        """Deliver an incoming event to the bound model for processing."""
        if self.model:
            self.model.receive(event)

    def log(self, message: str) -> None:
        """Record an application-level log event via the engine."""
        self.engine.log_app_event(self.id, message)
