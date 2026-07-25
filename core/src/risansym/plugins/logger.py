"""Console logging plugin."""

from __future__ import annotations

import logging

from risansym.event import Event, JsonPayload
from risansym.plugins.base import EngineContext, SimulationPlugin

logger = logging.getLogger("risansym")


class ConsoleLoggerPlugin(SimulationPlugin):
    """Log selected simulation events through the ``risansym`` logger.

    Args:
        trace_network: Display event scheduling and processing.
        app_logs: Display messages emitted through ``Model.log()``.
    """

    def __init__(self, trace_network: bool = False, app_logs: bool = False) -> None:
        self.trace_network = trace_network
        self.app_logs = app_logs

    def on_event_schedule(
        self,
        event: Event,
        context: EngineContext,
        node_state: JsonPayload | None = None,
    ) -> Event:
        if self.trace_network:
            logger.debug(
                "[t=%.1f] Node %d TRANSMITS '%s' -> Node %d (arrives at t=%.1f)",
                context.clock,
                event.source,
                event.name,
                event.target,
                event.time,
            )
        return event

    def on_event_processed(
        self,
        event: Event,
        node_state: JsonPayload,
        context: EngineContext,
    ) -> None:
        if self.trace_network:
            logger.debug(
                "[t=%.1f] Node %d RECEIVES '%s' <- Node %d",
                context.clock,
                event.target,
                event.name,
                event.source,
            )

    def on_app_log(self, source: int, message: str, context: EngineContext) -> None:
        if self.app_logs:
            logger.info("[t=%.1f] APP Node %d: %s", context.clock, source, message)
