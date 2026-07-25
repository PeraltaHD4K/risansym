from __future__ import annotations

from dataclasses import dataclass, field
import copy
import math
from typing import Union

from typing_extensions import TypeAliasType

from risansym.exceptions import InvalidEventError

# Type alias for JSON-serializable payloads exchanged between processes.
JsonValue = TypeAliasType(  # type: ignore[misc]
    "JsonValue",
    Union[str, int, float, bool, None, dict[str, "JsonValue"], list["JsonValue"]],  # type: ignore[misc]
)
JsonPayload = TypeAliasType("JsonPayload", dict[str, JsonValue])  # type: ignore[misc]


def _validate_json_value(value: object, path: str = "payload") -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if math.isfinite(value):
            return
        raise InvalidEventError(f"{path} contains a non-finite number.")
    if isinstance(value, list):
        for index, item in enumerate(value):
            _validate_json_value(item, f"{path}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise InvalidEventError(f"{path} keys must be strings.")
            _validate_json_value(item, f"{path}.{key}")
        return
    raise InvalidEventError(f"{path} must contain only JSON values, got {type(value).__name__}.")


@dataclass(order=True, slots=True, frozen=True)
class Event:
    """Encapsulates the information exchanged between active processes in the simulation.

    Args:
        time: Simulation time at which the event is scheduled.
        name: Human-readable name identifying the event type.
        source: Node ID of the sender.
        target: Node ID of the receiver.
        payload: JSON-serializable data attached to the event. The mapping is
            deep-copied on construction, so later mutations of the input do not
            alter the scheduled event. Treat ``event.payload`` as read-only.

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
        if not isinstance(self.payload, dict):
            raise InvalidEventError("Event payload must be a dictionary.")
        _validate_json_value(self.payload)
        object.__setattr__(self, "payload", copy.deepcopy(self.payload))

    def __repr__(self) -> str:
        return f"Event(t={self.time}, '{self.name}' {self.source}→{self.target})"
