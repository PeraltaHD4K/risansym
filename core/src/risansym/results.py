"""Result and lifecycle types shared by the simulation engine."""

from dataclasses import dataclass
from enum import Enum


class ScheduleResult(Enum):
    """Outcome of attempting to schedule an event."""

    SCHEDULED = "scheduled"
    DROPPED_TIME_HORIZON = "dropped_time_horizon"
    DROPPED_BY_PLUGIN = "dropped_by_plugin"


class SimulationState(Enum):
    """Lifecycle state of a :class:`risansym.simulation.Simulation`."""

    CREATED = "created"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    STOPPED = "stopped"
    FAILED = "failed"


class TerminationReason(Enum):
    """Reason why an execution call returned control to its caller."""

    AGENDA_EMPTY = "agenda_empty"
    MAX_EVENTS = "max_events"
    MAX_TIME = "max_time"
    TIME_LIMIT = "time_limit"
    STOP_REQUESTED = "stop_requested"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class SimulationResult:
    """Immutable snapshot of a simulation execution outcome."""

    state: SimulationState
    reason: TerminationReason
    simulated_time: float
    processed_events: int
    pending_events: int
    scheduled_events: int
    dropped_by_time_horizon: int
    dropped_by_plugins: int
    execution_real_time_seconds: float

    @property
    def complete(self) -> bool:
        """Whether the simulation reached a terminal successful state."""
        return self.state is SimulationState.COMPLETED
