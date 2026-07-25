from __future__ import annotations

import warnings
from pathlib import Path
from types import TracebackType
from typing import Any

from risansym.engine.builder import SimulationBuilder
from risansym.engine.loop import EventLoop
from risansym.event import Event
from risansym.model import Model
from risansym.plugins.base import SimulationPlugin
from risansym.simulator import Simulator
from risansym.topology import load_adjacency_matrix, load_edge_list, load_dense_matrix


class Simulation:
    """Global orchestrator (Facade) for the computational graph and simulation cycle.

    Creates processes, binds algorithm models, and drives the event loop until completion.
    
    Use the `from_file` classmethod to instantiate directly from a topology file.

    Args:
        graph: The adjacency-list representing the topology graph.
        maxtime: Maximum simulation time horizon.
        algo_name: Human-readable algorithm identifier for trace metadata.
        debug: (Deprecated) Replaced by trace_network and app_logs.
        trace_network: If ``True``, print every network event (TRANSMIT/RECEIVE) to stdout.
        app_logs: If ``True``, print application-level logs (self.log) to stdout.
        trace_enabled: Controls trace output — ``False`` disables tracing, ``True``
            auto-generates a file path unless ``trace_path`` is set.
        trace_path: Optional explicit output path for the trace file.
        trace_dir: Base directory for auto-generated trace files.
        trace_tag: Optional tag appended to the auto-generated filename.
        max_events: Hard limit on the number of events to process in the event loop.
    """

    def __init__(
        self,
        graph: list[list[int]] | str | Path,
        maxtime: float,
        algo_name: str = "UnknownAlgo",
        debug: bool | None = None,
        trace_network: bool = False,
        app_logs: bool = True,
        trace_enabled: bool = False,
        trace_path: str | Path | None = None,
        trace_dir: str = "traces",
        trace_tag: str | None = None,
        trace: bool | None = None,
        max_events: int = 10_000_000,
    ) -> None:

        # Backwards compatibility: accept deprecated 'debug' kwarg
        if debug is not None:
            warnings.warn(
                "The 'debug' argument is deprecated. Use 'trace_network' and 'app_logs' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            trace_network = debug
            app_logs = debug

        # Backwards compatibility: accept deprecated 'trace' kwarg
        if trace is not None:
            warnings.warn(
                "The 'trace' argument is deprecated. Use 'trace_enabled' instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            trace_enabled = trace

        self.algo_name = algo_name
        self._initialized = False
        self.max_events = max_events

        self.engine = Simulator(maxtime)
        
        # Build topology and processes using the new Builder
        self.graph, self._topology_name = SimulationBuilder.build_topology(graph)
        self.table = SimulationBuilder.build_processes(self.graph, self.engine)

        self.execution_metrics: dict[str, Any] = {}

        # Backwards compatibility auto-attach
        if trace_network or app_logs:
            from risansym.plugins.logger import ConsoleLoggerPlugin
            self.attach(ConsoleLoggerPlugin(trace_network=trace_network, app_logs=app_logs))
            
        if trace_enabled:
            from risansym.plugins.tracer import JSONTracerPlugin
            self.attach(JSONTracerPlugin(trace_path=trace_path, trace_dir=trace_dir, trace_tag=trace_tag))

    def attach(self, plugin: SimulationPlugin) -> None:
        """Attach a plugin (middleware) to the simulation."""
        self.engine.attach(plugin)

    def __repr__(self) -> str:
        nodes = len(self.table) - 1
        return f"<Simulation(algo='{self.algo_name}', topology='{self._topology_name}', nodes={nodes})>"

    @classmethod
    def from_file(
        cls,
        filename: str | Path,
        maxtime: float,
        algo_name: str = "UnknownAlgo",
        debug: bool | None = None,
        trace_network: bool = False,
        app_logs: bool = True,
        trace_enabled: bool = False,
        trace_path: str | Path | None = None,
        trace_dir: str = "traces",
        trace_tag: str | None = None,
        trace: bool | None = None,
        format: str = "adjacency_list",
        max_events: int = 10_000_000,
    ) -> Simulation:
        """Factory method to instantiate a Simulation from a topology file."""
        if format == "adjacency_list":
            graph = load_adjacency_matrix(filename)
        elif format == "edge_list":
            graph = load_edge_list(filename)
        elif format == "dense_matrix":
            graph = load_dense_matrix(filename)
        else:
            raise ValueError(f"Unknown topology format: {format}")
            
        instance = cls(
            graph=graph,
            maxtime=maxtime,
            algo_name=algo_name,
            debug=debug,
            trace_network=trace_network,
            app_logs=app_logs,
            trace_enabled=trace_enabled,
            trace_path=trace_path,
            trace_dir=trace_dir,
            trace_tag=trace_tag,
            trace=trace,
            max_events=max_events,
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

    def seed_event(self, event: Event) -> None:
        """Manually insert a seed event into the simulation engine."""
        self.engine.insert_event(event)

    def init(self, event: Event) -> None:
        """Deprecated: Use seed_event() instead."""
        warnings.warn(
            "Simulation.init() is deprecated and will be removed in v1.0. Use seed_event() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.seed_event(event)

    def _execute(self) -> None:
        """Main loop: pop and route events until the agenda is empty."""
        try:
            for plugin in self.engine._plugins:
                plugin.on_start(self)
                
            loop = EventLoop(self.engine, self.table, max_events=self.max_events)
            self.execution_metrics = loop.run()
        finally:
            for plugin in self.engine._plugins:
                try:
                    plugin.on_end(self)
                except Exception as e:
                    import logging
                    logging.getLogger(__name__).error(
                        "Plugin %s failed during on_end: %s", plugin.__class__.__name__, e
                    )



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

    def __enter__(self) -> Simulation:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        pass
