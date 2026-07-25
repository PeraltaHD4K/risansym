"""Result types shared by the simulation engine."""

from enum import Enum


class ScheduleResult(Enum):
    """Outcome of attempting to schedule an event."""

    SCHEDULED = "scheduled"
    DROPPED_TIME_HORIZON = "dropped_time_horizon"
    DROPPED_BY_PLUGIN = "dropped_by_plugin"
