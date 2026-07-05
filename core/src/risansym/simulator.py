from __future__ import annotations

import heapq
from typing import Any, TYPE_CHECKING

from risansym.event import Event
from risansym.schemas import TransmitEvent, AppLogEvent

if TYPE_CHECKING:
    from risansym.trace import TraceCollector


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

    def insert_event(self, event: Event, node_state: dict[str, Any] | None = None) -> None:
        """Push an event onto the heap if it falls within the time horizon."""
        if event.time <= self.maxtime:
            heapq.heappush(self._agenda, event)
            if self.debug:
                print(f"[t={self.clock:.1f}] Node {event.source} TRANSMITS '{event.name}' -> Node {event.target} (arrives at t={event.time:.1f})")

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
            print(f"[t={self.clock:.1f}] Node {event.target} RECEIVES '{event.name}' <- Node {event.source}")

        # Note: ReceiveEvent recording is done in Simulation._execute()
        # to capture the node state AFTER processing the event.
        return event

    def log_app_event(self, source: int, message: str) -> None:
        """Record an application-level log event in the trace."""
        if self.debug:
            print(f"[t={self.clock:.1f}] APP Node {source}: {message}")

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
