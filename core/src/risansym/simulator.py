from __future__ import annotations

import heapq
import math
from risansym.event import Event, JsonPayload
from risansym.exceptions import (
    CausalityError,
    ConfigurationError,
    InvalidEventError,
    SimulationError,
    SimulationLimitReached,
)
from risansym.plugins.base import EngineContext
from risansym.plugins.manager import PluginManager
from risansym.results import ScheduleResult


class Simulator:
    """Min-heap driven discrete event simulation engine.

    Maintains a priority queue (agenda) of :class:`Event` objects ordered
    by time. Events scheduled for the exact same time are processed in
    strict FIFO (first-in, first-out) order using a monotonic sequence number.
    Scheduling returns a :class:`~risansym.results.ScheduleResult`, so callers
    can distinguish accepted events from events rejected by the time horizon
    or a plugin.
    """

    def __init__(
        self,
        maxtime: float,
        *,
        plugin_manager: PluginManager | None = None,
        max_agenda_size: int | None = None,
    ) -> None:
        if not isinstance(maxtime, (int, float)) or isinstance(maxtime, bool):
            raise ConfigurationError("maxtime must be a number.")
        if not math.isfinite(maxtime) or maxtime <= 0:
            raise ConfigurationError("maxtime must be finite and greater than zero.")
        if max_agenda_size is not None and (
            not isinstance(max_agenda_size, int)
            or isinstance(max_agenda_size, bool)
            or max_agenda_size < 1
        ):
            raise ConfigurationError("max_agenda_size must be a positive integer or None.")
        self.clock: float = 0.0
        self.maxtime: float = float(maxtime)
        self.max_agenda_size = max_agenda_size
        self._agenda: list[tuple[float, int, Event]] = []
        self._sequence: int = 0
        self.plugin_manager = plugin_manager or PluginManager()
        self.scheduled_events = 0
        self.dropped_by_time_horizon = 0
        self.dropped_by_plugins = 0

    @property
    def requires_state_snapshot(self) -> bool:
        """Return whether any enabled plugin requires state snapshots."""
        return self.plugin_manager.requires_state_snapshot

    @property
    def pending_events(self) -> int:
        """Number of events currently waiting in the agenda."""
        return len(self._agenda)

    @property
    def next_event_time(self) -> float | None:
        """Scheduled time of the next event, if one exists."""
        return self._agenda[0][0] if self._agenda else None

    def context(self) -> EngineContext:
        """Build the immutable context exposed to plugins."""
        return EngineContext(
            clock=self.clock,
            maxtime=self.maxtime,
            pending_events=self.pending_events,
            scheduled_events=self.scheduled_events,
            dropped_by_time_horizon=self.dropped_by_time_horizon,
            dropped_by_plugins=self.dropped_by_plugins,
        )

    def checkpoint(self) -> tuple[list[tuple[float, int, Event]], int, int, int, int]:
        """Capture mutable scheduling state for transactional initialization."""
        return (
            list(self._agenda),
            self._sequence,
            self.scheduled_events,
            self.dropped_by_time_horizon,
            self.dropped_by_plugins,
        )

    def restore(
        self,
        checkpoint: tuple[list[tuple[float, int, Event]], int, int, int, int],
    ) -> None:
        """Restore a checkpoint created by :meth:`checkpoint`."""
        (
            self._agenda,
            self._sequence,
            self.scheduled_events,
            self.dropped_by_time_horizon,
            self.dropped_by_plugins,
        ) = checkpoint

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
        node_state: JsonPayload | None = None,
    ) -> ScheduleResult:
        """Validate and push an event onto the agenda."""
        event = self._validate_event(event)
        if event.time > self.maxtime:
            self.dropped_by_time_horizon += 1
            return ScheduleResult.DROPPED_TIME_HORIZON

        transformed = self.plugin_manager.transform_scheduled_event(
            event,
            self.context(),
            node_state,
            self._validate_event,
        )
        if transformed is None:
            self.dropped_by_plugins += 1
            return ScheduleResult.DROPPED_BY_PLUGIN
        event = self._validate_event(transformed)
        if event.time > self.maxtime:
            self.dropped_by_time_horizon += 1
            return ScheduleResult.DROPPED_TIME_HORIZON
        if self.max_agenda_size is not None and len(self._agenda) >= self.max_agenda_size:
            raise SimulationLimitReached(
                f"Agenda limit of {self.max_agenda_size} pending events reached."
            )

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
        self.plugin_manager.notify_app_log(source, message, self.context())

    @property
    def is_on(self) -> bool:
        """``True`` while there are pending events in the agenda."""
        return bool(self._agenda)
