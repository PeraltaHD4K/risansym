from pydantic import BaseModel, Field
from typing import Any, Literal, Union


class TransmitEvent(BaseModel):
    """Recorded when a node schedules a message for transmission."""

    action: Literal["TRANSMIT"] = "TRANSMIT"
    clock: float = Field(..., description="Time at which the sender dispatched the event")
    event_time: float = Field(..., description="Computed arrival time at the target node")
    source: int
    target: int
    name: str
    payload: Any
    node_state: dict[str, Any] | None = None


class ReceiveEvent(BaseModel):
    """Recorded when a node processes an incoming message."""

    action: Literal["RECEIVE"] = "RECEIVE"
    clock: float = Field(..., description="Time at which the node processes the event")
    source: int
    target: int
    name: str
    payload: Any
    node_state: dict[str, Any] | None = None


class AppLogEvent(BaseModel):
    """Recorded when a node emits an application-level log message."""

    action: Literal["APP_LOG"] = "APP_LOG"
    clock: float
    source: int
    message: str


# Union of all valid trace event types
TraceEvent = Union[TransmitEvent, ReceiveEvent, AppLogEvent]


class TraceMetadata(BaseModel):
    """Metadata attached to a complete simulation trace."""

    schema_version: Literal["1.0"] = "1.0"
    algorithm: str
    topology: str
    tag: str | None = None
    execution_date: str
    parameters: dict[str, Any]
    metrics: dict[str, Any]


class TraceOutput(BaseModel):
    """Top-level container for a simulation trace file."""

    metadata: TraceMetadata
    trace: list[TraceEvent]
