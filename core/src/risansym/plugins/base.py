"""Public plugin contracts and immutable callback contexts."""

from __future__ import annotations

from dataclasses import dataclass

from risansym.event import Event, JsonPayload
from risansym.results import SimulationResult, SimulationState


@dataclass(frozen=True, slots=True)
class EngineContext:
    """Read-only engine information exposed to plugins."""

    clock: float
    maxtime: float
    pending_events: int
    scheduled_events: int
    dropped_by_time_horizon: int
    dropped_by_plugins: int


@dataclass(frozen=True, slots=True)
class SimulationContext:
    """Read-only simulation information exposed to lifecycle plugins."""

    algorithm: str
    topology: str
    graph: tuple[tuple[int, ...], ...]
    model_types: tuple[str | None, ...]
    directed: bool
    maxtime: float
    state: SimulationState
    result: SimulationResult | None


class SimulationPlugin:
    """Base class for simulation plugins.

    Subclasses override only the callbacks they need. All callbacks execute in
    registration order.
    """

    @property
    def requires_state_snapshot(self) -> bool:
        return False

    def on_start(self, context: SimulationContext) -> None:
        """Called once, immediately before the first execution."""

    def on_event_schedule(
        self,
        event: Event,
        context: EngineContext,
        node_state: JsonPayload | None = None,
    ) -> Event | None:
        """Transform, accept, or drop an event before agenda insertion."""
        return event

    def on_event_processed(
        self,
        event: Event,
        node_state: JsonPayload,
        context: EngineContext,
    ) -> None:
        """Called after a model processes an event."""

    def on_app_log(self, source: int, message: str, context: EngineContext) -> None:
        """Called when a model emits an application log."""

    def on_end(self, context: SimulationContext) -> None:
        """Called once after completion or failure."""
