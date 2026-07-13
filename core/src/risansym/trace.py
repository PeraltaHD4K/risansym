from __future__ import annotations
from typing import Iterator

from pathlib import Path
from risansym.schemas import TraceEvent, TraceMetadata, TraceOutput


class TraceCollector:
    """Accumulates and persists the trace of simulated events using Pydantic models."""

    def __init__(self) -> None:
        self._trace: list[TraceEvent] = []

    def __repr__(self) -> str:
        return f"<TraceCollector(events={len(self._trace)})>"

    def record(self, entry: TraceEvent) -> None:
        """Append a structured event to the in-memory trace."""
        self._trace.append(entry)

    def get_event_count(self) -> int:
        """Return the number of recorded events.
        
        Deprecated: use len(collector) instead.
        """
        import warnings
        warnings.warn("get_event_count() is deprecated. Use len() instead.", DeprecationWarning, stacklevel=2)
        return len(self._trace)

    def __len__(self) -> int:
        return len(self._trace)

    def __bool__(self) -> bool:
        return True

    def __iter__(self) -> Iterator[TraceEvent]:
        return iter(self._trace)

    def dump(self, filepath: Path, metadata: TraceMetadata) -> None:
        """Validate and persist the trace to a JSON file on disk."""
        filepath.parent.mkdir(parents=True, exist_ok=True)

        output = TraceOutput(metadata=metadata, trace=self._trace)

        with filepath.open('w', encoding='utf-8') as f:
            f.write(output.model_dump_json())
