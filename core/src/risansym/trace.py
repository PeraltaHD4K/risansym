from __future__ import annotations

import warnings
from collections import deque
from typing import Iterator

from risansym.exceptions import ConfigurationError
from risansym.schemas import TraceEvent


_DEFAULT_MAX_EVENTS = 1_000_000


class TraceCollector:
    """Accumulates and persists the trace of simulated events using Pydantic models.

    Args:
        max_events: Maximum number of events to keep in memory, from 1 through
            1,000,000. When exceeded, the oldest events are discarded and a
            warning is emitted.
    """

    def __init__(self, max_events: int = _DEFAULT_MAX_EVENTS) -> None:
        if (
            not isinstance(max_events, int)
            or isinstance(max_events, bool)
            or not 1 <= max_events <= _DEFAULT_MAX_EVENTS
        ):
            raise ConfigurationError("max_events must be an integer from 1 through 1,000,000.")
        self._trace: deque[TraceEvent] = deque(maxlen=max_events)
        self._max_events = max_events
        self._overflow_warned = False
        self._total_events = 0

    def __repr__(self) -> str:
        return f"<TraceCollector(events={len(self._trace)})>"

    def record(self, entry: TraceEvent) -> None:
        """Append a structured event to the in-memory trace.

        If the collector has reached ``max_events``, the oldest event is
        dropped and a one-time warning is emitted.
        """
        self._total_events += 1
        if len(self._trace) == self._max_events:
            if not self._overflow_warned:
                warnings.warn(
                    f"TraceCollector has reached its limit of {self._max_events:,} events. "
                    "Oldest events are being discarded. Increase 'max_events' "
                    "to retain a larger window.",
                    ResourceWarning,
                    stacklevel=2,
                )
                self._overflow_warned = True
        self._trace.append(entry)

    def __len__(self) -> int:
        return len(self._trace)

    @property
    def total_events(self) -> int:
        """Total number of events presented to the collector."""
        return self._total_events

    @property
    def dropped_events(self) -> int:
        """Number of oldest events discarded due to the configured cap."""
        return self._total_events - len(self._trace)

    @property
    def max_events(self) -> int:
        """Configured in-memory event cap."""
        return self._max_events

    def __bool__(self) -> bool:
        """Always returns True to indicate the collector *exists*.

        This allows ``if self.collector:`` to check for the presence of a
        collector rather than whether it contains events.  Use ``len()`` to
        check whether events have been recorded.
        """
        return True

    def __iter__(self) -> Iterator[TraceEvent]:
        return iter(self._trace)
