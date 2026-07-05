from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

from risansym.event import Event

if TYPE_CHECKING:
    from risansym.process import Process


class Model(ABC):
    """Abstract interface (contract) for distributed algorithms.

    Subclasses must implement ``init()`` and ``receive()`` to define
    the node's state-machine logic.

    Attributes:
        clock: Current simulation time as seen by this node.
        process: Back-reference to the hosting ``Process`` (set during binding).
        neighbors: List of adjacent node IDs in the topology graph.
        id: Unique identifier of the node this model is bound to.
    """

    def __init__(self) -> None:
        self.clock: float = 0.0
        self.process: Process | None = None
        self.neighbors: list[int] = []
        self.id: int = 0

    # ------------------------------------------------------------------
    # Internal setters — called by the framework, not by user algorithms
    # ------------------------------------------------------------------

    def set_time(self, time: float) -> None:
        """Advance the node's local clock (called by the framework)."""
        self.clock = time

    def set_process(self, process: Process, neighbors: list[int], node_id: int) -> None:
        """Bind this model to its host process and topology context (called by the framework)."""
        self.process = process
        self.neighbors = neighbors
        self.id = node_id

    # ------------------------------------------------------------------
    # Public API for user algorithms
    # ------------------------------------------------------------------

    def transmit(self, event: Event) -> None:
        """Schedule a message transmission to another node."""
        if self.process:
            self.process.transmit(event)

    def log(self, message: str) -> None:
        """Record an application-level log event in the trace.

        Use this instead of ``print()`` so that log entries appear in the
        trace output and are visible in the web visualizer.
        """
        if self.process:
            self.process.log(message)

    def get_state(self) -> dict[str, Any]:
        """Return a snapshot of the node's internal state.

        Override in subclasses to expose algorithm-specific state that
        will be captured in the trace after each event is processed.
        """
        return {}

    @abstractmethod
    def init(self) -> None:
        """Initialize local state (implemented by the subclass)."""

    @abstractmethod
    def receive(self, event: Event) -> None:
        """State-machine transition logic (implemented by the subclass)."""
