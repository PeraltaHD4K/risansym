"""High-level discrete-event simulation lifecycle."""

from __future__ import annotations

import math
import warnings
from collections.abc import Sequence
from pathlib import Path

from risansym.engine.builder import SimulationBuilder
from risansym.engine.loop import EventLoop
from risansym.event import Event
from risansym.exceptions import ConfigurationError, SimulationError
from risansym.model import Model
from risansym.plugins.base import SimulationContext, SimulationPlugin
from risansym.plugins.manager import PluginFailurePolicy, PluginManager
from risansym.results import (
    ScheduleResult,
    SimulationResult,
    SimulationState,
    TerminationReason,
)
from risansym.simulator import Simulator
from risansym.topology import load_adjacency_list, load_dense_matrix, load_edge_list


class Simulation:
    """Orchestrate models, plugins, topology, and event-loop execution."""

    def __init__(
        self,
        graph: Sequence[Sequence[int]],
        maxtime: float,
        algo_name: str = "UnknownAlgo",
        directed: bool = False,
        trace_network: bool = False,
        app_logs: bool = False,
        trace_enabled: bool = False,
        trace_path: str | Path | None = None,
        trace_dir: str = "traces",
        trace_tag: str | None = None,
        max_events: int = 10_000_000,
        max_agenda_size: int | None = None,
        plugin_failure_policy: PluginFailurePolicy = PluginFailurePolicy.RAISE,
    ) -> None:
        self._validate_event_budget(max_events, "max_events")
        self.algo_name = algo_name
        self.directed = directed
        self.max_events = max_events
        self.state = SimulationState.CREATED
        self.result: SimulationResult | None = None
        self._processed_events = 0
        self._execution_real_time_seconds = 0.0
        self._plugins_started = False
        self._plugins_ended = False
        self._stop_requested = False

        self.plugin_manager = PluginManager(plugin_failure_policy)
        self.engine = Simulator(
            maxtime,
            plugin_manager=self.plugin_manager,
            max_agenda_size=max_agenda_size,
        )
        self.graph, self._topology_name = SimulationBuilder.build_topology(
            graph,
            directed=directed,
        )
        self.table = SimulationBuilder.build_processes(self.graph, self.engine)

        if trace_network or app_logs:
            from risansym.plugins.logger import ConsoleLoggerPlugin

            self.attach(ConsoleLoggerPlugin(trace_network=trace_network, app_logs=app_logs))
        if trace_enabled:
            from risansym.plugins.tracer import JSONTracerPlugin

            self.attach(
                JSONTracerPlugin(trace_path=trace_path, trace_dir=trace_dir, trace_tag=trace_tag)
            )

    @staticmethod
    def _validate_event_budget(value: int, name: str) -> None:
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise ConfigurationError(f"{name} must be a positive integer.")

    def _require_state(self, *allowed: SimulationState) -> None:
        if self.state not in allowed:
            expected = ", ".join(state.value for state in allowed)
            raise SimulationError(
                f"Operation is not valid while simulation is {self.state.value}; "
                f"expected one of: {expected}."
            )

    def _context(self) -> SimulationContext:
        return SimulationContext(
            algorithm=self.algo_name,
            topology=self._topology_name,
            graph=tuple(tuple(neighbors) for neighbors in self.graph),
            model_types=tuple(
                type(process.model).__name__ if process and process.model else None
                for process in self.table[1:]
            ),
            directed=self.directed,
            maxtime=self.engine.maxtime,
            state=self.state,
            result=self.result,
        )

    def attach(
        self,
        plugin: SimulationPlugin,
        *,
        failure_policy: PluginFailurePolicy | None = None,
    ) -> None:
        """Attach a plugin before initialization begins."""
        self._require_state(SimulationState.CREATED)
        self.plugin_manager.attach(plugin, policy=failure_policy)

    @property
    def plugins(self) -> tuple[SimulationPlugin, ...]:
        """Registered plugins as a read-only tuple."""
        return self.plugin_manager.plugins

    def __repr__(self) -> str:
        return (
            f"<Simulation(algo='{self.algo_name}', topology='{self._topology_name}', "
            f"nodes={len(self.graph)}, state='{self.state.value}')>"
        )

    @classmethod
    def from_file(
        cls,
        filename: str | Path,
        maxtime: float,
        algo_name: str = "UnknownAlgo",
        directed: bool = False,
        trace_network: bool = False,
        app_logs: bool = False,
        trace_enabled: bool = False,
        trace_path: str | Path | None = None,
        trace_dir: str = "traces",
        trace_tag: str | None = None,
        format: str = "adjacency_list",
        node_count: int | None = None,
        max_events: int = 10_000_000,
        max_agenda_size: int | None = None,
        plugin_failure_policy: PluginFailurePolicy = PluginFailurePolicy.RAISE,
    ) -> Simulation:
        """Build a simulation from a validated topology file."""
        if format == "adjacency_list":
            if node_count is not None:
                raise ConfigurationError("node_count is only valid for edge-list topologies.")
            graph = load_adjacency_list(filename, directed=directed)
        elif format == "edge_list":
            graph = load_edge_list(filename, directed=directed, node_count=node_count)
        elif format == "dense_matrix":
            if node_count is not None:
                raise ConfigurationError("node_count is only valid for edge-list topologies.")
            graph = load_dense_matrix(filename, directed=directed)
        else:
            raise ConfigurationError(f"Unknown topology format: {format}")

        instance = cls(
            graph=graph,
            maxtime=maxtime,
            algo_name=algo_name,
            directed=directed,
            trace_network=trace_network,
            app_logs=app_logs,
            trace_enabled=trace_enabled,
            trace_path=trace_path,
            trace_dir=trace_dir,
            trace_tag=trace_tag,
            max_events=max_events,
            max_agenda_size=max_agenda_size,
            plugin_failure_policy=plugin_failure_policy,
        )
        instance._topology_name = Path(filename).stem
        return instance

    def set_model(self, model: Model, node_id: int) -> None:
        """Bind one model while the simulation is in ``CREATED`` state."""
        self._require_state(SimulationState.CREATED)
        if not isinstance(model, Model):
            raise ConfigurationError(f"model must be a Model, got {type(model).__name__}.")
        if node_id < 1 or node_id >= len(self.table):
            raise ConfigurationError(f"Node {node_id} does not exist in the topology.")
        process = self.table[node_id]
        if process is None:
            raise SimulationError(f"Node {node_id} has no process.")
        if process.model is not None:
            raise ConfigurationError(f"Node {node_id} already has a model bound.")
        process.set_model(model)

    def initialize_all(self) -> None:
        """Initialize all bound models as one lifecycle transition."""
        self._require_state(SimulationState.CREATED)
        checkpoint = self.engine.checkpoint()
        self.state = SimulationState.INITIALIZING
        for node_id, process in enumerate(self.table[1:], start=1):
            if process is None or process.model is None:
                continue
            try:
                process.model.init()
            except Exception as error:
                self.engine.restore(checkpoint)
                self.state = SimulationState.FAILED
                raise SimulationError(
                    f"Model initialization failed at node {node_id}: {error}"
                ) from error
        self.state = SimulationState.READY

    def seed_event(self, event: Event) -> ScheduleResult:
        """Insert an event before or between execution calls."""
        self._require_state(SimulationState.READY, SimulationState.STOPPED)
        return self.engine.insert_event(event)

    def request_stop(self) -> None:
        """Request cooperative termination at the next event boundary."""
        self._require_state(SimulationState.RUNNING)
        self._stop_requested = True

    def _build_result(self, reason: TerminationReason) -> SimulationResult:
        return SimulationResult(
            state=self.state,
            reason=reason,
            simulated_time=self.engine.clock,
            processed_events=self._processed_events,
            pending_events=self.engine.pending_events,
            scheduled_events=self.engine.scheduled_events,
            dropped_by_time_horizon=self.engine.dropped_by_time_horizon,
            dropped_by_plugins=self.engine.dropped_by_plugins,
            execution_real_time_seconds=self._execution_real_time_seconds,
        )

    def _notify_end(self) -> None:
        if self._plugins_started and not self._plugins_ended:
            self._plugins_ended = True
            self.plugin_manager.notify_end(self._context())

    def _execute(
        self,
        *,
        max_events: int,
        until: float | None = None,
    ) -> SimulationResult:
        self._require_state(SimulationState.READY, SimulationState.STOPPED)
        self._stop_requested = False
        self.state = SimulationState.RUNNING

        try:
            if not self._plugins_started:
                self.plugin_manager.notify_start(self._context())
                self._plugins_started = True
            loop_result = EventLoop(self.engine, self.table).run(
                max_events=max_events,
                until=until,
                stop_requested=lambda: self._stop_requested,
            )
            self._processed_events += loop_result.processed_events
            self._execution_real_time_seconds += loop_result.execution_real_time_seconds
            if loop_result.reason in (
                TerminationReason.AGENDA_EMPTY,
                TerminationReason.MAX_TIME,
            ):
                self.state = SimulationState.COMPLETED
            else:
                self.state = SimulationState.STOPPED
            self.result = self._build_result(loop_result.reason)
            if self.state is SimulationState.COMPLETED:
                self._notify_end()
            return self.result
        except Exception:
            self.state = SimulationState.FAILED
            self.result = self._build_result(TerminationReason.ERROR)
            self._notify_end()
            raise

    def run(self, *, max_events: int | None = None) -> SimulationResult:
        """Run until completion or an event budget is exhausted."""
        self._require_state(SimulationState.READY, SimulationState.STOPPED)
        budget = self.max_events if max_events is None else max_events
        self._validate_event_budget(budget, "max_events")
        self._warn_unbound_models()
        return self._execute(max_events=budget)

    def step(self) -> SimulationResult:
        """Process at most one event."""
        self._require_state(SimulationState.READY, SimulationState.STOPPED)
        self._warn_unbound_models()
        return self._execute(max_events=1)

    def run_until(self, time: float, *, max_events: int | None = None) -> SimulationResult:
        """Run without processing events scheduled after ``time``."""
        self._require_state(SimulationState.READY, SimulationState.STOPPED)
        if not isinstance(time, (int, float)) or isinstance(time, bool) or not math.isfinite(time):
            raise ConfigurationError("time must be a finite number.")
        if time < self.engine.clock:
            raise ConfigurationError("time cannot be earlier than the current simulation clock.")
        if time > self.engine.maxtime:
            raise ConfigurationError("time cannot exceed the simulation maxtime.")
        budget = self.max_events if max_events is None else max_events
        self._validate_event_budget(budget, "max_events")
        self._warn_unbound_models()
        return self._execute(max_events=budget, until=float(time))

    def _warn_unbound_models(self) -> None:
        unbound = [
            node_id
            for node_id, process in enumerate(self.table[1:], start=1)
            if process is not None and process.model is None
        ]
        if unbound:
            warnings.warn(
                f"Nodes {unbound} have no model bound. "
                "Events targeting these nodes will be ignored.",
                UserWarning,
                stacklevel=3,
            )
