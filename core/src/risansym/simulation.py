from __future__ import annotations

import datetime
import time
import warnings
from pathlib import Path
from typing import Any

from risansym.event import Event
from risansym.model import Model
from risansym.process import Process
from risansym.simulator import Simulator
from risansym.schemas import TraceMetadata, ReceiveEvent


class Simulation:
    """Global orchestrator for the computational graph and simulation cycle.

    Creates processes, binds algorithm models, and drives the event loop until completion.
    
    Use the `from_file` classmethod to instantiate directly from a topology file.

    Args:
        graph: The adjacency-list representing the topology graph.
        maxtime: Maximum simulation time horizon.
        algo_name: Human-readable algorithm identifier for trace metadata.
        debug: If ``True``, print event-by-event debug output to stdout.
        trace: Controls trace output — ``False`` disables tracing, ``True``
            auto-generates a file path, or a ``str``/``Path`` sets the output path.
        trace_dir: Base directory for auto-generated trace files.
        trace_tag: Optional tag appended to the auto-generated filename.
    """

    def __init__(
        self,
        graph: list[list[int]] | str | Path,
        maxtime: float,
        algo_name: str = "UnknownAlgo",
        debug: bool = True,
        trace: bool | str | Path = False,
        trace_dir: str = "traces",
        trace_tag: str | None = None,
    ) -> None:
        from risansym.trace import TraceCollector

        self.algo_name = algo_name
        self.trace = trace
        self.trace_dir = trace_dir
        self.trace_tag = trace_tag
        self._topology_name = "unknown_topology"
        self._initialized = False

        self.collector = TraceCollector() if trace else None
        self.engine = Simulator(maxtime, debug=debug, collector=self.collector)
        
        # Backwards compatibility: Duck typing the constructor
        if isinstance(graph, (str, Path)):
            warnings.warn(
                "Passing a filename directly to Simulation() is deprecated "
                "and will be removed in v1.0. Use Simulation.from_file() instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            self.graph = self._load_adjacency_matrix(graph)
            self._topology_name = Path(graph).stem
        else:
            self.graph = graph

        self.execution_metrics: dict[str, Any] = {}

        # Index 0 reserved as None; nodes are 1-indexed
        self.table: list[Process | None] = [None] + [
            Process(row, self.engine, i)
            for i, row in enumerate(self.graph, start=1)
        ]

    def __repr__(self) -> str:
        nodes = len(self.table) - 1
        return f"<Simulation(algo='{self.algo_name}', topology='{self._topology_name}', nodes={nodes})>"

    @classmethod
    def from_file(
        cls,
        filename: str | Path,
        maxtime: float,
        algo_name: str = "UnknownAlgo",
        debug: bool = True,
        trace: bool | str | Path = False,
        trace_dir: str = "traces",
        trace_tag: str | None = None,
    ) -> Simulation:
        """Factory method to instantiate a Simulation from a topology file."""
        graph = cls._load_adjacency_matrix(filename)
        instance = cls(
            graph=graph,
            maxtime=maxtime,
            algo_name=algo_name,
            debug=debug,
            trace=trace,
            trace_dir=trace_dir,
            trace_tag=trace_tag,
        )
        instance._topology_name = Path(filename).stem
        return instance

    @staticmethod
    def _load_adjacency_matrix(filename: str | Path) -> list[list[int]]:
        """Build the topology G=(V,E) from file, with format validation.

        Raises:
            FileNotFoundError: If the topology file does not exist.
            ValueError: If the file contains non-integer tokens or
                references nodes outside the valid range.
        """
        path = Path(filename)
        if not path.exists():
            raise FileNotFoundError(f"Topology file '{path}' does not exist.")

        graph: list[list[int]] = []
        line_idx = 0
        try:
            for line_idx, line in enumerate(path.read_text().splitlines()):
                if not line.strip():
                    continue
                neighbors = [int(node) for node in line.split()]
                graph.append(neighbors)
        except ValueError as e:
            raise ValueError(
                f"Syntax error in topology file (line {line_idx + 1}): "
                f"all node identifiers must be integers. ({e})"
            ) from e

        # Validate that references do not point to out-of-range nodes
        num_nodes = len(graph)
        for i, neighbors in enumerate(graph, start=1):
            for neighbor in neighbors:
                if neighbor < 1 or neighbor > num_nodes:
                    raise ValueError(
                        f"Node {i} references node {neighbor}, which is outside "
                        f"the valid range (1 to {num_nodes})."
                    )

        return graph

    def set_model(self, model: Model, node_id: int) -> None:
        """Bind an algorithm model to a specific node.

        Raises:
            IndexError: If ``node_id`` is outside the topology.
        """
        if node_id < 1 or node_id >= len(self.table):
            raise IndexError(f"Node {node_id} does not exist in the topology.")
        if process := self.table[node_id]:
            process.set_model(model)

    def initialize_all(self) -> None:
        """Initialize all bound models.

        Call this **after** all models have been assigned via :meth:`set_model`
        to ensure the full topology is available when ``Model.init()`` runs.
        """
        self._initialized = True
        for process in self.table:
            if process and process.model:
                process.model.init()

    def init(self, event: Event) -> None:
        """Manually insert a seed event into the simulation engine."""
        self.engine.insert_event(event)

    def _execute(self) -> None:
        """Main loop: pop and route events until the agenda is empty."""
        start_real_time = time.perf_counter()

        while self.engine.is_on:
            event = self.engine.pop_event()
            if process := self.table[event.target]:
                process.set_time(event.time)
                process.receive(event)

                # Snapshot the node's internal state AFTER processing
                state = process.model.get_state() if process.model else {}

                if self.collector:
                    self.collector.record(ReceiveEvent(
                        action="RECEIVE",
                        clock=event.time,
                        source=event.source,
                        target=event.target,
                        name=event.name,
                        payload=event.payload,
                        node_state=state
                    ))

        end_real_time = time.perf_counter()

        self.execution_metrics = {
            "simulated_time_elapsed": self.engine.clock,
            "total_messages": self.collector.get_event_count() if self.collector else 0,
            "execution_real_time_sec": round(end_real_time - start_real_time, 5)
        }

    def _save_trace(self) -> None:
        """Serialize and persist the trace with metadata."""
        graph_name = self._topology_name
        tag = f"_{self.trace_tag}" if self.trace_tag else ""
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")

        if isinstance(self.trace, (str, Path)) and not isinstance(self.trace, bool):
            trace_path = Path(self.trace)
        else:
            file_name = f"{self.algo_name}_{graph_name}{tag}_{timestamp}.json"
            trace_path = Path(self.trace_dir) / self.algo_name / file_name

        total_edges = sum(len(neighbors) for neighbors in self.graph)
        total_nodes = len(self.table) - 1

        metadata = TraceMetadata(
            schema_version="1.0",
            algorithm=self.algo_name,
            topology=graph_name,
            tag=self.trace_tag,
            execution_date=timestamp,
            parameters={
                "max_time": self.engine.maxtime,
                "total_nodes": total_nodes,
                "total_edges": total_edges
            },
            metrics=self.execution_metrics
        )

        if self.collector:
            self.collector.dump(trace_path, metadata)

    def run(self) -> None:
        """Entry point: execute the simulation and optionally save the trace."""
        if not self._initialized:
            warnings.warn(
                "Calling run() without calling initialize_all() is deprecated. "
                "Models were auto-initialized, but you must do this explicitly in v1.0.",
                DeprecationWarning,
                stacklevel=2,
            )
            self.initialize_all()

        self._execute()
        if self.trace:
            self._save_trace()
