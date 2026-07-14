from __future__ import annotations

import warnings
from pathlib import Path
from types import TracebackType
from typing import Any

from risansym.engine.builder import SimulationBuilder
from risansym.engine.exporter import TraceExporter
from risansym.engine.loop import EventLoop
from risansym.event import Event
from risansym.model import Model
from risansym.simulator import Simulator
from risansym.topology import load_adjacency_matrix


class Simulation:
    """Global orchestrator (Facade) for the computational graph and simulation cycle.

    Creates processes, binds algorithm models, and drives the event loop until completion.
    
    Use the `from_file` classmethod to instantiate directly from a topology file.

    Args:
        graph: The adjacency-list representing the topology graph.
        maxtime: Maximum simulation time horizon.
        algo_name: Human-readable algorithm identifier for trace metadata.
        debug: If ``True``, print event-by-event debug output to stdout.
        trace_enabled: Controls trace output — ``False`` disables tracing, ``True``
            auto-generates a file path unless ``trace_path`` is set.
        trace_path: Optional explicit output path for the trace file.
        trace_dir: Base directory for auto-generated trace files.
        trace_tag: Optional tag appended to the auto-generated filename.
    """

    def __init__(
        self,
        graph: list[list[int]] | str | Path,
        maxtime: float,
        algo_name: str = "UnknownAlgo",
        debug: bool = True,
        trace_enabled: bool = False,
        trace_path: str | Path | None = None,
        trace_dir: str = "traces",
        trace_tag: str | None = None,
        trace: bool | None = None,
    ) -> None:
        from risansym.trace import TraceCollector

        # Backwards compatibility: accept deprecated 'trace' kwarg
        if trace is not None:
            warnings.warn(
                "The 'trace' argument is deprecated. Use 'trace_enabled' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            trace_enabled = trace

        self.algo_name = algo_name
        self.trace_enabled = trace_enabled
        self.trace_path = trace_path
        self.trace_dir = trace_dir
        self.trace_tag = trace_tag
        self._initialized = False

        self.collector = TraceCollector() if trace_enabled else None
        self.engine = Simulator(maxtime, debug=debug, collector=self.collector)
        
        # Build topology and processes using the new Builder
        self.graph, self._topology_name = SimulationBuilder.build_topology(graph)
        self.table = SimulationBuilder.build_processes(self.graph, self.engine)

        self.execution_metrics: dict[str, Any] = {}
        self._trace_saved = False

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
        trace_enabled: bool = False,
        trace_path: str | Path | None = None,
        trace_dir: str = "traces",
        trace_tag: str | None = None,
    ) -> Simulation:
        """Factory method to instantiate a Simulation from a topology file."""
        graph = load_adjacency_matrix(filename)
        instance = cls(
            graph=graph,
            maxtime=maxtime,
            algo_name=algo_name,
            debug=debug,
            trace_enabled=trace_enabled,
            trace_path=trace_path,
            trace_dir=trace_dir,
            trace_tag=trace_tag,
        )
        instance._topology_name = Path(filename).stem
        return instance

    def set_model(self, model: Model, node_id: int) -> None:
        """Bind an algorithm model to a specific node.

        Raises:
            IndexError: If ``node_id`` is outside the topology.
            ValueError: If the node already has a model bound.
        """
        if node_id < 1 or node_id >= len(self.table):
            raise IndexError(f"Node {node_id} does not exist in the topology.")
        if process := self.table[node_id]:
            if process.model is not None:
                raise ValueError(f"Node {node_id} already has a model bound.")
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
        loop = EventLoop(self.engine, self.table, self.collector)
        self.execution_metrics = loop.run()

    def _save_trace(self) -> None:
        """Serialize and persist the trace with metadata."""
        if not self.collector:
            return
            
        exporter = TraceExporter(
            algo_name=self.algo_name,
            topology_name=self._topology_name,
            graph=self.graph,
            table=self.table,
            maxtime=self.engine.maxtime,
            trace_path=self.trace_path,
            trace_dir=self.trace_dir,
            trace_tag=self.trace_tag,
        )
        exporter.export(self.collector, self.execution_metrics)

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

        # Warn about nodes without bound models
        unbound = [
            i for i, p in enumerate(self.table)
            if p is not None and p.model is None
        ]
        if unbound:
            warnings.warn(
                f"Nodes {unbound} have no model bound. "
                f"Events targeting these nodes will be silently ignored.",
                UserWarning,
                stacklevel=2,
            )

        self._execute()
        if self.trace_enabled:
            self._save_trace()
            self._trace_saved = True

    def __enter__(self) -> Simulation:
        self._trace_saved = False
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if self.trace_enabled and not self._trace_saved:
            self._save_trace()
