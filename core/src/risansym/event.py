from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import TypeAlias, Union

from risansym.exceptions import InvalidEventError

# Type alias for JSON-serializable payloads exchanged between processes.
JsonValue: TypeAlias = Union[str, int, float, bool, None, dict[str, "JsonValue"], list["JsonValue"]]
JsonPayload: TypeAlias = dict[str, JsonValue]


@dataclass(order=True, slots=True, frozen=True)
class Event:
    """Encapsulates the information exchanged between active processes in the simulation.

    Args:
        time: Simulation time at which the event is scheduled.
        name: Human-readable name identifying the event type.
        source: Node ID of the sender.
        target: Node ID of the receiver.
        payload: Optional JSON-serializable data attached to the event.
                 Note: Although the Event class is frozen, the payload dict is
                 mutable. Callers should avoid mutating it after creation.

    Note on event ordering:
        Events scheduled for the exact same time are processed in FIFO order
        (the order in which they were inserted into the simulator).
    """

    time: float
    # field(compare=False) prevents tie-breaking by name/IDs when times are equal
    name: str = field(compare=False)
    source: int = field(compare=False)
    target: int = field(compare=False)
    payload: JsonPayload = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.time, (int, float)) or isinstance(self.time, bool):
            raise InvalidEventError("Event time must be a number.")
        if not math.isfinite(self.time) or self.time < 0:
            raise InvalidEventError(
                f"Invalid event time: {self.time}. Time must be finite and non-negative."
            )
        if not isinstance(self.source, int) or isinstance(self.source, bool) or self.source < 1:
            raise InvalidEventError("Event source must be a positive integer.")
        if not isinstance(self.target, int) or isinstance(self.target, bool) or self.target < 1:
            raise InvalidEventError("Event target must be a positive integer.")
        if not isinstance(self.name, str) or not self.name:
            raise InvalidEventError("Event name must be a non-empty string.")

    def __repr__(self) -> str:
        return f"Event(t={self.time}, '{self.name}' {self.source}→{self.target})"
