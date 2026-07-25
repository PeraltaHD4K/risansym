from __future__ import annotations

import heapq
import logging
import math
from typing import Any

from risansym.event import Event
from risansym.exceptions import (
    CausalityError,
    ConfigurationError,
    InvalidEventError,
    SimulationError,
)
from risansym.plugins.base import SimulationPlugin
from risansym.results import ScheduleResult

logger = logging.getLogger(__name__)


class Simulator:
    """Min-heap driven discrete event simulation engine.

    Maintains a priority queue (agenda) of :class:`Event` objects ordered
    by time. Events scheduled for the exact same time are processed in
    strict FIFO (first-in, first-out) order using a monotonic sequence number.
    Scheduling returns a :class:`~risansym.results.ScheduleResult`, so callers
    can distinguish accepted events from events rejected by the time horizon
    or a plugin.
    """

    def __init__(self, maxtime: float) -> None:
        if not isinstance(maxtime, (int, float)) or isinstance(maxtime, bool):
            raise ConfigurationError("maxtime must be a number.")
        if not math.isfinite(maxtime) or maxtime <= 0:
            raise ConfigurationError("maxtime must be finite and greater than zero.")
        self.clock: float = 0.0
        self.maxtime: float = float(maxtime)
        self._agenda: list[tuple[float, int, Event]] = []
        self._sequence: int = 0
        self._plugins: list[SimulationPlugin] = []
        self.scheduled_events = 0
        self.dropped_by_time_horizon = 0
        self.dropped_by_plugins = 0

    def attach(self, plugin: SimulationPlugin) -> None:
        """Attach a plugin to the simulator."""
        self._plugins.append(plugin)

    def notify_plugins_start(self, simulation: Any) -> None:
        """Notify all attached plugins that the simulation is starting."""
        for plugin in self._plugins:
            plugin.on_start(simulation)

    def notify_plugins_end(self, simulation: Any) -> None:
        """Notify all attached plugins that the simulation has ended."""
        for plugin in self._plugins:
            try:
                plugin.on_end(simulation)
            except Exception as e:
                logger.error("Plugin %s failed during on_end: %s", plugin.__class__.__name__, e)

    @property
    def requires_state_snapshot(self) -> bool:
        """Returns True if any attached plugin requires state snapshots."""
        return any(getattr(p, "requires_state_snapshot", False) for p in self._plugins)

    def __repr__(self) -> str:
        return f"<Simulator(clock={self.clock}, agenda_size={len(self._agenda)})>"

    def _validate_event(self, event: object) -> Event:
        """Validate an event against the simulator's current temporal state."""
        if not isinstance(event, Event):
            raise InvalidEventError(
                f"Plugins must return Event or None, got {type(event).__name__}."
            )
        if event.time < self.clock:
            raise CausalityError(
                f"Cannot schedule event at t={event.time} when clock is at t={self.clock}."
            )
        return event

    def insert_event(
        self,
        event: Event,
        node_state: dict[str, Any] | None = None,
    ) -> ScheduleResult:
        """Validate and push an event onto the agenda."""
        event = self._validate_event(event)
        if event.time > self.maxtime:
            self.dropped_by_time_horizon += 1
            return ScheduleResult.DROPPED_TIME_HORIZON

        for plugin in self._plugins:
            transformed = plugin.on_event_schedule(event, self, node_state)
            if transformed is None:
                self.dropped_by_plugins += 1
                return ScheduleResult.DROPPED_BY_PLUGIN
            event = self._validate_event(transformed)
            if event.time > self.maxtime:
                self.dropped_by_time_horizon += 1
                return ScheduleResult.DROPPED_TIME_HORIZON

        heapq.heappush(self._agenda, (event.time, self._sequence, event))
        self._sequence += 1
        self.scheduled_events += 1
        return ScheduleResult.SCHEDULED

    def pop_event(self) -> Event:
        """Pop the nearest event and advance the global clock.

        Raises:
            SimulationError: If the agenda is empty.
        """
        if not self._agenda:
            raise SimulationError("Cannot pop from an empty event agenda.")
        _, _, event = heapq.heappop(self._agenda)
        self.clock = event.time

        # Note: ReceiveEvent recording is done in Simulation._execute()
        # to capture the node state AFTER processing the event.
        return event

    def log_app_event(self, source: int, message: str) -> None:
        """Record an application-level log event in the trace."""
        for plugin in self._plugins:
            plugin.on_app_log(source, message, self.clock, self)

    @property
    def is_on(self) -> bool:
        """``True`` while there are pending events in the agenda."""
        return bool(self._agenda)
