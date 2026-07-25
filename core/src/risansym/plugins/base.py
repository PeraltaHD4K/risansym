from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from risansym.event import Event
    from risansym.simulation import Simulation
    from risansym.simulator import Simulator


@runtime_checkable
class SimulationPlugin(Protocol):
    """Base protocol for Risansym simulation plugins (middlewares).

    Plugins can hook into various lifecycle events of the simulation engine
    to implement tracing, logging, network chaos, metrics, etc.
    """

    @property
    def requires_state_snapshot(self) -> bool:
        """If True, the engine will deepcopy the node state for this plugin."""
        return False

    def on_start(self, simulation: Simulation) -> None:
        """Called just before the simulation event loop begins."""
        ...

    def on_event_schedule(
        self, event: Event, simulator: Simulator, node_state: dict[str, Any] | None = None
    ) -> Event | None:
        """Called when an event is about to be inserted into the agenda.

        Args:
            event: The event attempting to be scheduled.
            simulator: The Simulator instance.
            node_state: Snapshot of the node's state at the moment of transmission.

        Returns:
            The event to be scheduled, or `None` if the event should be dropped (e.g., packet loss).
        """
        return event

    def on_event_processed(
        self, event: Event, node_state: dict[str, Any], simulator: Simulator
    ) -> None:
        """Called after an event has been successfully processed by a node.

        Args:
            event: The processed event.
            node_state: Deep copy snapshot of the node's state AFTER processing.
            simulator: The Simulator instance.
        """
        ...

    def on_app_log(self, source: int, message: str, clock: float, simulator: Simulator) -> None:
        """Called when a node emits an application-level log."""
        ...

    def on_end(self, simulation: Simulation) -> None:
        """Called when the simulation loop has finished."""
        ...
