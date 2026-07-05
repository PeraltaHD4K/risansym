from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# Type alias for JSON-serializable payloads exchanged between processes.
JsonPayload = dict[str, Any]


@dataclass(order=True, slots=True)
class Event:
    """Encapsulates the information exchanged between active processes in the simulation."""

    time: float
    # field(compare=False) prevents tie-breaking by name/IDs when times are equal
    name: str = field(compare=False)
    target: int = field(compare=False)
    source: int = field(compare=False)
    payload: JsonPayload = field(default_factory=dict, compare=False)

    def __repr__(self) -> str:
        return f"Event(t={self.time}, '{self.name}' {self.source}→{self.target})"
