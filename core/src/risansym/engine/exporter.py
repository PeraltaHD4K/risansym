from __future__ import annotations

import datetime
import re
import uuid
from pathlib import Path
from typing import Any

from risansym.exceptions import TraceExportError
from risansym.schemas import TraceMetadata
from risansym.trace import TraceCollector


class TraceExporter:
    """Handles serialization and persistence of the simulation trace."""

    def __init__(
        self,
        algo_name: str,
        topology_name: str,
        graph: list[list[int]],
        directed: bool,
        model_types: tuple[str | None, ...],
        maxtime: float,
        trace_path: str | Path | None = None,
        trace_dir: str = "traces",
        trace_tag: str | None = None,
    ) -> None:
        self.algo_name = algo_name
        self.topology_name = topology_name
        self.graph = graph
        self.directed = directed
        self.model_types = model_types
        self.maxtime = maxtime
        self.trace_path = trace_path
        self.trace_dir = trace_dir
        self.trace_tag = trace_tag

    def export(self, collector: TraceCollector, metrics: dict[str, Any]) -> Path:
        """Serialize and persist the trace with metadata."""

        def sanitize(name: str | None) -> str:
            if not name:
                return ""
            # Allow alphanumeric, dot, underscore, dash. Replace others with underscore.
            return re.sub(r"[^A-Za-z0-9._-]", "_", name)[:64]

        safe_algo = sanitize(self.algo_name)
        safe_topo = sanitize(self.topology_name)
        safe_tag = f"_{sanitize(self.trace_tag)}" if self.trace_tag else ""

        now = datetime.datetime.now(datetime.timezone.utc)
        timestamp = now.strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:6]

        if self.trace_path:
            trace_path = Path(self.trace_path)
        else:
            file_name = f"{safe_algo}_{safe_topo}{safe_tag}_{timestamp}_{unique_id}.json"
            base_dir = Path(self.trace_dir).resolve()
            trace_path = (base_dir / safe_algo / file_name).resolve()

            # Ensure we didn't somehow escape trace_dir
            if not trace_path.is_relative_to(base_dir):
                raise ValueError("Generated trace path escapes the intended directory.")

        adjacency_entries = sum(len(neighbors) for neighbors in self.graph)
        total_edges = adjacency_entries if self.directed else adjacency_entries // 2
        total_nodes = len(self.model_types)

        metadata = TraceMetadata(
            schema_version="1.0",
            algorithm=self.algo_name,
            topology=self.topology_name,
            tag=self.trace_tag,
            execution_date=now,
            parameters={
                "max_time": self.maxtime,
                "total_nodes": total_nodes,
                "total_edges": total_edges,
                "directed": self.directed,
            },
            metrics=metrics,
        )

        try:
            collector.dump(trace_path, metadata)
        except Exception as error:
            raise TraceExportError(f"Could not export trace to '{trace_path}': {error}") from error
        return trace_path
