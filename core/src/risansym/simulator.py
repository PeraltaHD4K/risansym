from __future__ import annotations

import heapq
import logging
from typing import Any

from risansym.event import Event

from risansym.plugins.base import SimulationPlugin

logger = logging.getLogger(__name__)


class Simulator:
    """Min-heap driven discrete event simulation engine.

    Maintains a priority queue (agenda) of :class:`Event` objects ordered
    by time.  Events beyond ``maxtime`` are silently discarded.
    """

    def __init__(self, maxtime: float) -> None:
        if maxtime <= 0:
            raise ValueError("maxtime must be greater than 0")
        self.clock: float = 0.0
        self.maxtime: float = maxtime
        self._agenda: list[Event] = []
        self._plugins: list[SimulationPlugin] = []

    def attach(self, plugin: SimulationPlugin) -> None:
        """Attach a plugin to the simulator."""
        self._plugins.append(plugin)
        
    @property
    def requires_state_snapshot(self) -> bool:
        """Returns True if any attached plugin requires state snapshots."""
        return any(getattr(p, "requires_state_snapshot", False) for p in self._plugins)

    def __repr__(self) -> str:
        return f"<Simulator(clock={self.clock}, agenda_size={len(self._agenda)})>"

    def insert_event(self, event: Event, node_state: dict[str, Any] | None = None) -> None:
        """Push an event onto the heap if it falls within the time horizon."""
        if event.time < self.clock:
            raise ValueError(f"Causality violation: Cannot schedule event at t={event.time} when clock is at t={self.clock}")
        if event.time <= self.maxtime:
            for plugin in self._plugins:
                event_or_none = plugin.on_event_schedule(event, self, node_state)
                if event_or_none is None:
                    return
                event = event_or_none

            heapq.heappush(self._agenda, event)

    def pop_event(self) -> Event:
        """Pop the nearest event and advance the global clock.

        Raises:
            RuntimeError: If the agenda is empty.
        """
        if not self._agenda:
            raise RuntimeError("Cannot pop from an empty event agenda.")
        event = heapq.heappop(self._agenda)
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
