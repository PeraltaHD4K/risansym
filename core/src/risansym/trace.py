from __future__ import annotations

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
        """Return the number of recorded events."""
        return len(self._trace)

    def dump(self, filepath: Path, metadata: TraceMetadata) -> None:
        """Validate and persist the trace to a JSON file on disk."""
        filepath.parent.mkdir(parents=True, exist_ok=True)

        output = TraceOutput(metadata=metadata, trace=self._trace)

        with filepath.open('w', encoding='utf-8') as f:
            f.write(output.model_dump_json(indent=2))
