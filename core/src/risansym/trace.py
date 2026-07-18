from __future__ import annotations

import warnings
from typing import Iterator
from collections import deque

from pathlib import Path
from risansym.schemas import TraceEvent, TraceMetadata


_DEFAULT_MAX_EVENTS = 1_000_000


class TraceCollector:
    """Accumulates and persists the trace of simulated events using Pydantic models.

    Args:
        max_events: Maximum number of events to keep in memory. When exceeded,
            the oldest events are discarded and a warning is emitted. Defaults
            to 1,000,000. Set to ``None`` for unlimited (not recommended for
            large simulations).
    """

    def __init__(self, max_events: int | None = _DEFAULT_MAX_EVENTS) -> None:
        self._trace: deque[TraceEvent] = deque(maxlen=max_events)
        self._max_events = max_events
        self._overflow_warned = False

    def __repr__(self) -> str:
        return f"<TraceCollector(events={len(self._trace)})>"

    def record(self, entry: TraceEvent) -> None:
        """Append a structured event to the in-memory trace.

        If the collector has reached ``max_events``, the oldest event is
        dropped and a one-time warning is emitted.
        """
        if self._max_events is not None and len(self._trace) == self._max_events:
            if not self._overflow_warned:
                warnings.warn(
                    f"TraceCollector has reached its limit of {self._max_events:,} events. "
                    f"Oldest events are being discarded. Increase 'max_events' or set "
                    f"it to None to disable this limit (not recommended).",
                    ResourceWarning,
                    stacklevel=2,
                )
                self._overflow_warned = True
        self._trace.append(entry)

    def get_event_count(self) -> int:
        """Return the number of recorded events.
        
        Deprecated: use len(collector) instead.
        """
        warnings.warn("get_event_count() is deprecated. Use len() instead.", DeprecationWarning, stacklevel=2)
        return len(self._trace)

    def __len__(self) -> int:
        return len(self._trace)

    def __bool__(self) -> bool:
        """Always returns True to indicate the collector *exists*.

        This allows ``if self.collector:`` to check for the presence of a
        collector rather than whether it contains events.  Use ``len()`` to
        check whether events have been recorded.
        """
        return True

    def __iter__(self) -> Iterator[TraceEvent]:
        return iter(self._trace)

    def dump(self, filepath: Path, metadata: TraceMetadata) -> None:
        """Validate and persist the trace to a JSON file on disk.
        
        Uses streaming JSON serialization to avoid doubling memory usage
        for large traces.
        """
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # We serialize manually to achieve true streaming and avoid loading
        # the entire trace array into RAM as a single string (OOM risk).
        with filepath.open('w', encoding='utf-8') as f:
            f.write('{"metadata":')
            f.write(metadata.model_dump_json())
            f.write(',"trace":[')
            
            for i, event in enumerate(self._trace):
                if i > 0:
                    f.write(',')
                f.write(event.model_dump_json())
            
            f.write(']}')
