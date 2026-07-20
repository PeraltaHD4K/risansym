from pydantic import BaseModel, Field, ConfigDict
from typing import Literal, Annotated
import datetime
from risansym.event import JsonPayload, JsonValue

class TransmitEvent(BaseModel):
    """Recorded when a node schedules a message for transmission."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    action: Literal["TRANSMIT"] = "TRANSMIT"
    clock: float = Field(..., description="Time at which the sender dispatched the event")
    event_time: float = Field(..., description="Computed arrival time at the target node")
    source: int
    target: int
    name: str
    payload: JsonPayload
    node_state: JsonPayload | None = None


class ReceiveEvent(BaseModel):
    """Recorded when a node processes an incoming message."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    action: Literal["RECEIVE"] = "RECEIVE"
    clock: float = Field(..., description="Time at which the node processes the event")
    source: int
    target: int
    name: str
    payload: JsonPayload
    node_state: JsonPayload | None = None


class AppLogEvent(BaseModel):
    """Recorded when a node emits an application-level log message."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    action: Literal["APP_LOG"] = "APP_LOG"
    clock: float
    source: int
    message: str


# Union of all valid trace event types
TraceEvent = Annotated[
    TransmitEvent | ReceiveEvent | AppLogEvent,
    Field(discriminator="action")
]


class TraceMetadata(BaseModel):
    """Metadata attached to a complete simulation trace."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    algorithm: str
    topology: str
    tag: str | None = None
    execution_date: datetime.datetime
    parameters: JsonPayload
    metrics: JsonPayload


class TraceOutput(BaseModel):
    """Top-level container for a simulation trace file."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    metadata: TraceMetadata
    trace: list[TraceEvent]

TransmitEvent.model_rebuild()
ReceiveEvent.model_rebuild()
TraceMetadata.model_rebuild()
TraceOutput.model_rebuild()
