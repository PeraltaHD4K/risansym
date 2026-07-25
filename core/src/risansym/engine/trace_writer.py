"""Atomic persistence for validated JSON traces."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterable
from pathlib import Path

from risansym.schemas import TraceEvent, TraceMetadata


class AtomicJSONTraceWriter:
    """Stream a trace to disk and publish it with an atomic replace."""

    def write(
        self,
        filepath: Path,
        metadata: TraceMetadata,
        events: Iterable[TraceEvent],
    ) -> None:
        filepath = filepath.resolve()
        filepath.parent.mkdir(parents=True, exist_ok=True)
        temporary_path: Path | None = None
        try:
            descriptor, temporary_name = tempfile.mkstemp(
                dir=filepath.parent,
                prefix=f".{filepath.name}.",
                suffix=".tmp",
            )
            temporary_path = Path(temporary_name)
            with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
                stream.write('{"metadata":')
                stream.write(metadata.model_dump_json())
                stream.write(',"trace":[')
                for index, event in enumerate(events):
                    if index:
                        stream.write(",")
                    stream.write(event.model_dump_json())
                stream.write("]}")
                stream.flush()
                os.fsync(stream.fileno())
            temporary_path.replace(filepath)
        except Exception:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
            raise
