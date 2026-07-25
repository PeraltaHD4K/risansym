from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from risansym.event import Event

if TYPE_CHECKING:
    from risansym.simulation import Simulation
    from risansym.simulator import Simulator

logger = logging.getLogger("risansym")

class ConsoleLoggerPlugin:
    """Logs simulation events to the standard output."""

    def __init__(self, trace_network: bool = False, app_logs: bool = True) -> None:
        self.trace_network = trace_network
        self.app_logs = app_logs
        
        # Configure logger for Jupyter / Colab compatibility
        if self.trace_network or self.app_logs:
            import sys
            target_level = logging.DEBUG if self.trace_network else logging.INFO
            logger.setLevel(target_level)

            if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
                ch = logging.StreamHandler(sys.stdout)
                ch.setLevel(target_level)
                ch.setFormatter(logging.Formatter('%(message)s'))
                logger.addHandler(ch)
                logger.propagate = False

    @property
    def requires_state_snapshot(self) -> bool:
        return False

    def on_start(self, simulation: Simulation) -> None:
        pass

    def on_event_schedule(self, event: Event, simulator: Simulator, node_state: dict[str, Any] | None = None) -> Event | None:
        if self.trace_network:
            logger.debug(
                "[t=%.1f] Node %d TRANSMITS '%s' -> Node %d (arrives at t=%.1f)",
                simulator.clock,
                event.source,
                event.name,
                event.target,
                event.time,
            )
        return event

    def on_event_processed(self, event: Event, node_state: dict[str, Any], simulator: Simulator) -> None:
        if self.trace_network:
            logger.debug(
                "[t=%.1f] Node %d RECEIVES '%s' <- Node %d",
                simulator.clock,
                event.target,
                event.name,
                event.source,
            )

    def on_app_log(self, source: int, message: str, clock: float, simulator: Simulator) -> None:
        if self.app_logs:
            logger.info("[t=%.1f] APP Node %d: %s", clock, source, message)

    def on_end(self, simulation: Simulation) -> None:
        pass
