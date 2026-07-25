from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from risansym.engine.exporter import TraceExporter
from risansym.event import Event
from risansym.schemas import AppLogEvent, ReceiveEvent, TransmitEvent
from risansym.trace import TraceCollector

if TYPE_CHECKING:
    from risansym.simulation import Simulation
    from risansym.simulator import Simulator


class JSONTracerPlugin:
    """Records simulation events and exports them to a JSON trace file."""

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

    def on_start(self, simulation: Simulation) -> None:
        pass

    def on_event_schedule(
        self, event: Event, simulator: Simulator, node_state: dict[str, Any] | None = None
    ) -> Event | None:
        self.collector.record(
            TransmitEvent.model_construct(
                action="TRANSMIT",
                clock=simulator.clock,
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
        self, event: Event, node_state: dict[str, Any], simulator: Simulator
    ) -> None:
        self.collector.record(
            ReceiveEvent.model_construct(
                action="RECEIVE",
                clock=simulator.clock,
                source=event.source,
                target=event.target,
                name=event.name,
                payload=event.payload,
                node_state=node_state,
            )
        )

    def on_app_log(self, source: int, message: str, clock: float, simulator: Simulator) -> None:
        self.collector.record(
            AppLogEvent.model_construct(
                action="APP_LOG", clock=clock, source=source, message=message
            )
        )

    def on_end(self, simulation: Simulation) -> None:
        exporter = TraceExporter(
            algo_name=simulation.algo_name,
            topology_name=simulation._topology_name,
            graph=simulation.graph,
            table=simulation.table,
            maxtime=simulation.engine.maxtime,
            trace_path=self.trace_path,
            trace_dir=self.trace_dir,
            trace_tag=self.trace_tag,
        )
        exporter.export(self.collector, simulation.execution_metrics)
