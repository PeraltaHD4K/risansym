from pydantic import BaseModel, Field
from typing import Any, Literal, Union

class TransmitEvent(BaseModel):
    action: Literal["TRANSMIT"] = "TRANSMIT"
    clock: float = Field(..., description="Tiempo en el que el emisor disparó el evento")
    event_time: float = Field(..., description="Tiempo calculado de llegada al destino")
    source: int
    target: int
    name: str
    payload: Any

class ReceiveEvent(BaseModel):
    action: Literal["RECEIVE"] = "RECEIVE"
    clock: float = Field(..., description="Tiempo en el que el nodo procesa el evento")
    source: int
    target: int
    name: str
    payload: Any

class AppLogEvent(BaseModel):
    action: Literal["APP_LOG"] = "APP_LOG"
    clock: float
    source: int
    message: str

# Agrupación de todos los eventos válidos
TraceEvent = Union[TransmitEvent, ReceiveEvent, AppLogEvent]

class TraceMetadata(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    algorithm: str
    topology: str
    tag: str | None = None
    execution_date: str
    parameters: dict[str, Any]
    metrics: dict[str, Any]

class TraceOutput(BaseModel):
    metadata: TraceMetadata
    trace: list[TraceEvent]
