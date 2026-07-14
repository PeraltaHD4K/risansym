from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol
import warnings

from risansym.event import Event


class MessageSink(Protocol):
    """Protocol defining what a Model needs from its host environment."""

    def transmit(self, event: Event) -> None: ...
    def log(self, message: str) -> None: ...


class Model(ABC):
    """Abstract interface (contract) for distributed algorithms.

    Subclasses must implement ``init()`` and ``receive()`` to define
    the node's state-machine logic.

    Attributes:
        clock: Current simulation time as seen by this node.
        sink: Back-reference to the hosting environment (set during binding).
        neighbors: List of adjacent node IDs in the topology graph.
        node_id: Unique identifier of the node this model is bound to.
    """

    def __init__(self) -> None:
        self.clock: float = 0.0
        self.sink: MessageSink | None = None
        self.neighbors: list[int] = []
        self.node_id: int = 0

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(node_id={self.node_id}, clock={self.clock})>"

    @property
    def id(self) -> int:
        warnings.warn(
            "Accessing 'Model.id' is deprecated and will be removed in v1.0. "
            "Use 'Model.node_id' instead to avoid shadowing the built-in id().",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.node_id

    @id.setter
    def id(self, value: int) -> None:
        warnings.warn(
            "Setting 'Model.id' is deprecated and will be removed in v1.0. "
            "Use 'Model.node_id' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.node_id = value

    # ------------------------------------------------------------------
    # Internal setters — called by the framework, not by user algorithms
    # ------------------------------------------------------------------

    def set_time(self, time: float) -> None:
        """Advance the node's local clock (called by the framework)."""
        if time < self.clock:
            raise ValueError(f"Time cannot go backwards (current: {self.clock}, new: {time})")
        self.clock = time

    def set_sink(self, sink: MessageSink, neighbors: list[int], node_id: int) -> None:
        """Bind this model to its host environment and topology context (called by the framework)."""
        self.sink = sink
        self.neighbors = list(neighbors)
        self.node_id = node_id

    # ------------------------------------------------------------------
    # Public API for user algorithms
    # ------------------------------------------------------------------

    def transmit(self, event: Event) -> None:
        """Schedule a message transmission to another node."""
        if self.sink is None:
            raise RuntimeError(
                f"Model(node_id={self.node_id}) cannot transmit: not bound to a Process. "
                "Ensure Simulation.initialize_all() has been called."
            )
        self.sink.transmit(event)

    def log(self, message: str) -> None:
        """Record an application-level log event in the trace.

        Use this instead of ``print()`` so that log entries appear in the
        trace output and are visible in the web visualizer.
        """
        if self.sink is None:
            raise RuntimeError(
                f"Model(node_id={self.node_id}) cannot log: not bound to a Process. "
                "Ensure Simulation.initialize_all() has been called."
            )
        self.sink.log(message)

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
