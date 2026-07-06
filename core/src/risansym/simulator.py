from __future__ import annotations

import heapq
import logging
from typing import Any, TYPE_CHECKING

from risansym.event import Event
from risansym.schemas import TransmitEvent, AppLogEvent

if TYPE_CHECKING:
    from risansym.trace import TraceCollector

logger = logging.getLogger(__name__)


class Simulator:
    """Min-heap driven discrete event simulation engine.

    Maintains a priority queue (agenda) of :class:`Event` objects ordered
    by time.  Events beyond ``maxtime`` are silently discarded.
    """

    def __init__(self, maxtime: float, debug: bool = True, collector: TraceCollector | None = None) -> None:
        self.clock: float = 0.0
        self.maxtime: float = maxtime
        self._agenda: list[Event] = []
        self.debug: bool = debug
        self._collector = collector

    def __repr__(self) -> str:
        return f"<Simulator(clock={self.clock}, agenda_size={len(self._agenda)})>"

    def insert_event(self, event: Event, node_state: dict[str, Any] | None = None) -> None:
        """Push an event onto the heap if it falls within the time horizon."""
        if event.time <= self.maxtime:
            heapq.heappush(self._agenda, event)
            if self.debug:
                logger.debug("[t=%.1f] Node %d TRANSMITS '%s' -> Node %d (arrives at t=%.1f)", self.clock, event.source, event.name, event.target, event.time)

            if self._collector:
                self._collector.record(TransmitEvent(
                    action="TRANSMIT",
                    clock=self.clock,
                    event_time=event.time,
                    source=event.source,
                    target=event.target,
                    name=event.name,
                    payload=event.payload,
                    node_state=node_state
                ))

    def pop_event(self) -> Event:
        """Pop the nearest event and advance the global clock."""
        event = heapq.heappop(self._agenda)
        self.clock = event.time
        if self.debug:
            logger.debug("[t=%.1f] Node %d RECEIVES '%s' <- Node %d", self.clock, event.target, event.name, event.source)

        # Note: ReceiveEvent recording is done in Simulation._execute()
        # to capture the node state AFTER processing the event.
        return event

    def log_app_event(self, source: int, message: str) -> None:
        """Record an application-level log event in the trace."""
        if self.debug:
            logger.info("[t=%.1f] APP Node %d: %s", self.clock, source, message)

        if self._collector:
            self._collector.record(AppLogEvent(
                action="APP_LOG",
                clock=self.clock,
                source=source,
                message=message
            ))

    @property
    def is_on(self) -> bool:
        """``True`` while there are pending events in the agenda."""
        return bool(self._agenda)
