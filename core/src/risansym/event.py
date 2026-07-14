from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypeAlias


# Type alias for JSON-serializable payloads exchanged between processes.
JsonPayload: TypeAlias = dict[str, Any]


@dataclass(order=True, slots=True, frozen=True)
class Event:
    """Encapsulates the information exchanged between active processes in the simulation.

    Args:
        time: Simulation time at which the event is scheduled.
        name: Human-readable name identifying the event type.
        source: Node ID of the sender.
        target: Node ID of the receiver.
        payload: Optional JSON-serializable data attached to the event.

    .. deprecated:: 0.5.2
        The old positional field order was ``(time, name, target, source)``.
        It has been corrected to ``(time, name, source, target)``.
        Code using keyword arguments is unaffected.
    """

    time: float
    # field(compare=False) prevents tie-breaking by name/IDs when times are equal
    name: str = field(compare=False)
    source: int = field(compare=False)
    target: int = field(compare=False)
    payload: JsonPayload = field(default_factory=dict, compare=False)

    def __repr__(self) -> str:
        return f"Event(t={self.time}, '{self.name}' {self.source}→{self.target})"
