import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from risansym.event import JsonPayload

NonNegativeTime = Annotated[float, Field(ge=0, allow_inf_nan=False)]
NodeId = Annotated[int, Field(gt=0)]
NonEmptyString = Annotated[str, Field(min_length=1)]


class TransmitEvent(BaseModel):
    """Recorded when a node schedules a message for transmission."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    action: Literal["TRANSMIT"] = "TRANSMIT"
    clock: NonNegativeTime = Field(description="Time at which the sender dispatched the event")
    event_time: NonNegativeTime = Field(description="Computed arrival time at the target node")
    source: NodeId
    target: NodeId
    name: NonEmptyString
    payload: JsonPayload
    node_state: JsonPayload | None = None

    @model_validator(mode="after")
    def validate_causality(self) -> "TransmitEvent":
        """Ensure the recorded arrival cannot precede transmission."""
        if self.event_time < self.clock:
            raise ValueError("event_time cannot be earlier than clock")
        return self


class ReceiveEvent(BaseModel):
    """Recorded when a node processes an incoming message."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    action: Literal["RECEIVE"] = "RECEIVE"
    clock: NonNegativeTime = Field(description="Time at which the node processes the event")
    source: NodeId
    target: NodeId
    name: NonEmptyString
    payload: JsonPayload
    node_state: JsonPayload | None = None


class AppLogEvent(BaseModel):
    """Recorded when a node emits an application-level log message."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    action: Literal["APP_LOG"] = "APP_LOG"
    clock: NonNegativeTime
    source: NodeId
    message: NonEmptyString


# Union of all valid trace event types
TraceEvent = Annotated[TransmitEvent | ReceiveEvent | AppLogEvent, Field(discriminator="action")]


class TraceCapture(BaseModel):
    """Describe trace retention and make truncation machine-readable."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    max_events: int = Field(gt=0, le=1_000_000)
    recorded_events: int = Field(ge=0)
    dropped_events: int = Field(ge=0)
    truncated: bool

    @model_validator(mode="after")
    def validate_counts(self) -> "TraceCapture":
        """Keep the truncation flag and counters internally consistent."""
        if self.truncated != (self.dropped_events > 0):
            raise ValueError("truncated must be true exactly when dropped_events is positive")
        return self


class TraceMetadata(BaseModel):
    """Metadata attached to a complete simulation trace."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    schema_version: Literal["1.0"] = "1.0"
    algorithm: NonEmptyString
    topology: NonEmptyString
    tag: str | None = None
    execution_date: datetime.datetime
    parameters: JsonPayload
    metrics: JsonPayload
    capture: TraceCapture


class TraceOutput(BaseModel):
    """Top-level container for a simulation trace file."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    metadata: TraceMetadata
    trace: Annotated[list[TraceEvent], Field(max_length=1_000_000)]

    @model_validator(mode="after")
    def validate_recorded_count(self) -> "TraceOutput":
        """Ensure capture metadata describes the serialized trace."""
        if self.metadata.capture.recorded_events != len(self.trace):
            raise ValueError("capture.recorded_events must equal trace length")
        return self
