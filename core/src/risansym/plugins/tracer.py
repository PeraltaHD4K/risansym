"""JSON tracing plugin."""

from __future__ import annotations

from pathlib import Path

from risansym.engine.exporter import TraceExporter
from risansym.event import Event
from risansym.plugins.base import EngineContext, SimulationContext, SimulationPlugin
from risansym.schemas import AppLogEvent, ReceiveEvent, TransmitEvent
from risansym.trace import TraceCollector


class JSONTracerPlugin(SimulationPlugin):
    """Record simulation events and export them to a JSON trace file."""

    def __init__(
        self,
        trace_path: str | Path | None = None,
        trace_dir: str = "traces",
        trace_tag: str | None = None,
    ) -> None:
        self.collector = TraceCollector()
        self.trace_path = trace_path
        self.trace_dir = trace_dir
        self.trace_tag = trace_tag
        self.exported_path: Path | None = None

    @property
    def requires_state_snapshot(self) -> bool:
        return True

    def on_event_schedule(
        self,
        event: Event,
        context: EngineContext,
        node_state: dict[str, object] | None = None,
    ) -> Event:
        self.collector.record(
            TransmitEvent(
                action="TRANSMIT",
                clock=context.clock,
                event_time=event.time,
                source=event.source,
                target=event.target,
                name=event.name,
                payload=event.payload,
                node_state=node_state,
            )
        )
        return event

    def on_event_processed(
        self,
        event: Event,
        node_state: dict[str, object],
        context: EngineContext,
    ) -> None:
        self.collector.record(
            ReceiveEvent(
                action="RECEIVE",
                clock=context.clock,
                source=event.source,
                target=event.target,
                name=event.name,
                payload=event.payload,
                node_state=node_state,
            )
        )

    def on_app_log(self, source: int, message: str, context: EngineContext) -> None:
        self.collector.record(
            AppLogEvent(
                action="APP_LOG",
                clock=context.clock,
                source=source,
                message=message,
            )
        )

    def on_end(self, context: SimulationContext) -> None:
        if context.result is None:
            return
        exporter = TraceExporter(
            algo_name=context.algorithm,
            topology_name=context.topology,
            graph=[list(neighbors) for neighbors in context.graph],
            directed=context.directed,
            model_types=context.model_types,
            maxtime=context.maxtime,
            trace_path=self.trace_path,
            trace_dir=self.trace_dir,
            trace_tag=self.trace_tag,
        )
        self.exported_path = exporter.export(
            self.collector,
            {
                "termination_reason": context.result.reason.value,
                "simulated_time_elapsed": context.result.simulated_time,
                "total_messages": context.result.processed_events,
                "execution_real_time_sec": round(
                    context.result.execution_real_time_seconds,
                    5,
                ),
                "scheduled_events": context.result.scheduled_events,
                "dropped_by_time_horizon": context.result.dropped_by_time_horizon,
                "dropped_by_plugins": context.result.dropped_by_plugins,
                "pending_events": context.result.pending_events,
            },
        )
