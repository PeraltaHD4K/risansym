"""Runtime coordination between the pure scheduler and simulation plugins."""

from __future__ import annotations

from dataclasses import dataclass

from risansym.event import Event, JsonPayload
from risansym.plugins.base import EngineContext, SimulationContext, SimulationPlugin
from risansym.plugins.manager import PluginFailurePolicy, PluginManager
from risansym.results import ScheduleResult
from risansym.simulator import SchedulerCheckpoint, Simulator


@dataclass(frozen=True, slots=True)
class RuntimeCheckpoint:
    """Internal snapshot of scheduler and plugin-related runtime counters."""

    scheduler: SchedulerCheckpoint
    dropped_by_plugins: int


class SimulationRuntime:
    """Adapt a pure scheduler to plugin-aware model execution."""

    def __init__(self, simulator: Simulator) -> None:
        self._simulator = simulator
        self._plugins = PluginManager()
        self.dropped_by_plugins = 0

    @property
    def clock(self) -> float:
        return self._simulator.clock

    @clock.setter
    def clock(self, value: float) -> None:
        self._simulator.clock = value

    @property
    def maxtime(self) -> float:
        return self._simulator.maxtime

    @property
    def pending_events(self) -> int:
        return self._simulator.pending_events

    @property
    def next_event_time(self) -> float | None:
        return self._simulator.next_event_time

    @property
    def scheduled_events(self) -> int:
        return self._simulator.scheduled_events

    @property
    def dropped_by_time_horizon(self) -> int:
        return self._simulator.dropped_by_time_horizon

    @property
    def requires_state_snapshot(self) -> bool:
        return self._plugins.requires_state_snapshot

    @property
    def plugins(self) -> tuple[SimulationPlugin, ...]:
        return self._plugins.plugins

    @property
    def is_on(self) -> bool:
        return self._simulator.is_on

    def context(self) -> EngineContext:
        return EngineContext(
            clock=self.clock,
            maxtime=self.maxtime,
            pending_events=self.pending_events,
            scheduled_events=self.scheduled_events,
            dropped_by_time_horizon=self.dropped_by_time_horizon,
            dropped_by_plugins=self.dropped_by_plugins,
        )

    def attach(
        self,
        plugin: SimulationPlugin,
        *,
        policy: PluginFailurePolicy | None = None,
    ) -> None:
        self._plugins.attach(plugin, policy=policy)

    def insert_event(
        self,
        event: Event,
        node_state: JsonPayload | None = None,
    ) -> ScheduleResult:
        event = self._simulator.validate_event(event)
        if event.time > self.maxtime:
            return self._simulator.insert_event(event)

        transformed = self._plugins.transform_scheduled_event(
            event,
            self.context(),
            node_state,
            self._simulator.validate_event,
        )
        if transformed is None:
            self.dropped_by_plugins += 1
            return ScheduleResult.DROPPED_BY_PLUGIN
        return self._simulator.insert_event(transformed)

    def pop_event(self) -> Event:
        return self._simulator.pop_event()

    def log_app_event(self, source: int, message: str) -> None:
        self._plugins.notify_app_log(source, message, self.context())

    def notify_event_processed(self, event: Event, node_state: JsonPayload) -> None:
        self._plugins.notify_event_processed(event, node_state, self.context())

    def notify_start(self, context: SimulationContext) -> None:
        self._plugins.notify_start(context)

    def notify_end(self, context: SimulationContext) -> None:
        self._plugins.notify_end(context)

    def checkpoint(self) -> RuntimeCheckpoint:
        return RuntimeCheckpoint(
            scheduler=self._simulator.checkpoint(),
            dropped_by_plugins=self.dropped_by_plugins,
        )

    def restore(self, checkpoint: RuntimeCheckpoint) -> None:
        self.dropped_by_plugins = checkpoint.dropped_by_plugins
        self._simulator.restore(checkpoint.scheduler)
