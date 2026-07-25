"""Internal event-loop execution primitives."""

from __future__ import annotations

import copy
import time
from collections.abc import Callable
from dataclasses import dataclass

from risansym.exceptions import InvalidEventError, SimulationError
from risansym.process import Process
from risansym.results import TerminationReason
from risansym.simulator import Simulator


@dataclass(frozen=True, slots=True)
class LoopResult:
    """Internal result for one event-loop invocation."""

    processed_events: int
    reason: TerminationReason
    execution_real_time_seconds: float


class EventLoop:
    """Route queued events until an explicit execution boundary is reached."""

    def __init__(
        self,
        simulator: Simulator,
        table: list[Process | None],
    ) -> None:
        self.simulator = simulator
        self.table = table

    def _process_next(self) -> None:
        event = self.simulator.pop_event()
        if event.target >= len(self.table):
            raise InvalidEventError(
                f"Event targets node {event.target}, but only nodes "
                f"1-{len(self.table) - 1} exist in the topology."
            )

        if process := self.table[event.target]:
            process._set_time(event.time)
            try:
                process.receive(event)
            except Exception as error:
                raise SimulationError(
                    f"Simulation crashed at node {event.target} while processing "
                    f"'{event.name}': {error}"
                ) from error

            if self.simulator.requires_state_snapshot:
                raw_state = process.model.get_state() if process.model else {}
                state = copy.deepcopy(raw_state)
            else:
                state = {}
            self.simulator.plugin_manager.notify_event_processed(
                event,
                state,
                self.simulator.context(),
            )

    def run(
        self,
        *,
        max_events: int,
        until: float | None = None,
        stop_requested: Callable[[], bool] | None = None,
    ) -> LoopResult:
        """Process events until the agenda or one requested limit is reached."""
        start = time.perf_counter()
        processed = 0

        while self.simulator.is_on:
            if stop_requested is not None and stop_requested():
                reason = TerminationReason.STOP_REQUESTED
                break
            if processed >= max_events:
                reason = TerminationReason.MAX_EVENTS
                break
            if until is not None and self.simulator.next_event_time is not None:
                if self.simulator.next_event_time > until:
                    reason = TerminationReason.TIME_LIMIT
                    break

            self._process_next()
            processed += 1
        else:
            reason = (
                TerminationReason.MAX_TIME
                if self.simulator.dropped_by_time_horizon
                else TerminationReason.AGENDA_EMPTY
            )

        return LoopResult(
            processed_events=processed,
            reason=reason,
            execution_real_time_seconds=time.perf_counter() - start,
        )
