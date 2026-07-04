from __future__ import annotations

from risansym.event import Event
from risansym.model import Model
from risansym.simulator import Simulator


class Process:
    """Entidad que reside en un vértice de la topología."""

    def __init__(self, neighbors: list[int], engine: Simulator, node_id: int) -> None:
        self.neighbors = neighbors
        self.engine = engine
        self.id = node_id
        self.model: Model | None = None

    def set_model(self, model: Model) -> None:
        self.model = model
        self.model.set_process(self, self.neighbors, self.id)
        self.model.init()

    def set_time(self, time: float) -> None:
        if self.model:
            self.model.set_time(time)

    def transmit(self, event: Event) -> None:
        state = self.model.get_state() if self.model else {}
        self.engine.insert_event(event, node_state=state)

    def receive(self, event: Event) -> None:
        if self.model:
            self.model.receive(event)

    def log(self, message: str) -> None:
        self.engine.log_app_event(self.id, message)
