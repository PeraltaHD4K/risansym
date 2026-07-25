from __future__ import annotations

import copy
import logging
from typing import Protocol

from risansym.event import Event, JsonPayload
from risansym.exceptions import InvalidEventError
from risansym.model import Model
from risansym.results import ScheduleResult


class EngineProtocol(Protocol):
    def insert_event(
        self,
        event: Event,
        node_state: JsonPayload | None = None,
    ) -> ScheduleResult: ...

    def log_app_event(self, source: int, message: str) -> None: ...

    @property
    def requires_state_snapshot(self) -> bool: ...


class Process:
    """Entity that resides at a vertex of the topology graph.

    A process hosts exactly one :class:`Model` and mediates communication
    between the model's algorithm logic and the simulation engine.
    """

    def __init__(self, neighbors: list[int], engine: EngineProtocol, node_id: int) -> None:
        self.neighbors = neighbors
        self.engine = engine
        self.node_id = node_id
        self.model: Model | None = None

    def __repr__(self) -> str:
        return f"<Process(node_id={self.node_id}, neighbors={self.neighbors})>"

    def _bind_model(self, model: Model) -> None:
        """Bind a model to this process without triggering initialization."""
        self.model = model
        self.model._bind(self, self.neighbors, self.node_id)

    def _set_time(self, time: float) -> None:
        """Forward the simulation clock to the bound model."""
        if self.model:
            self.model._set_time(time)

    def transmit(self, event: Event) -> ScheduleResult:
        """Delegate event insertion to the engine, attaching the node's current state."""
        if event.source != self.node_id:
            raise InvalidEventError(
                f"Process {self.node_id} cannot transmit an event with source {event.source}."
            )
        if event.target not in self.neighbors and event.target != self.node_id:
            raise InvalidEventError(
                f"Process {self.node_id} cannot transmit to {event.target}: not a neighbor."
            )

        if self.engine.requires_state_snapshot:
            state = self.model.get_state() if self.model else None
            if state is None:
                logging.getLogger(__name__).warning(
                    "Process %d transmitted an event without a bound model.", self.node_id
                )
                state = {}
            else:
                state = copy.deepcopy(state)
        else:
            state = {}

        return self.engine.insert_event(event, node_state=state)

    def receive(self, event: Event) -> None:
        """Deliver an incoming event to the bound model for processing."""
        if self.model:
            self.model.receive(event)
        else:
            logging.getLogger(__name__).warning(
                "Process %d received an event but has no bound model.", self.node_id
            )

    def log(self, message: str) -> None:
        """Record an application-level log event via the engine."""
        self.engine.log_app_event(self.node_id, message)
