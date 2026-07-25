from __future__ import annotations

import copy
import time
from typing import Any

from risansym.exceptions import InvalidEventError, SimulationError
from risansym.process import Process
from risansym.simulator import Simulator


class EventLoop:
    """Executes the simulation event loop and routes messages."""

    def __init__(
        self,
        simulator: Simulator,
        table: list[Process | None],
        max_events: int = 10_000_000,
    ) -> None:
        self.simulator = simulator
        self.table = table
        self.max_events = max_events

    def run(self) -> dict[str, Any]:
        """Main loop: pop and route events until the agenda is empty.

        Returns:
            Dictionary containing execution metrics.
        """
        start_real_time = time.perf_counter()
        processed_events = 0

        while self.simulator.is_on:
            if processed_events >= self.max_events:
                import logging

                logging.getLogger(__name__).warning(
                    f"Simulation aborted: Event budget of {self.max_events} exceeded."
                )
                break

            event = self.simulator.pop_event()

            if event.target < 1 or event.target >= len(self.table):
                raise InvalidEventError(
                    f"Event targets node {event.target}, but only nodes "
                    f"1-{len(self.table) - 1} exist in the topology."
                )

            if process := self.table[event.target]:
                process.set_time(event.time)

                try:
                    process.receive(event)
                # Note: Catching 'Exception' is safe here. It catches application errors
                # but naturally allows 'SystemExit' and 'KeyboardInterrupt' (which inherit
                # from 'BaseException') to bubble up and terminate the simulation.
                except Exception as error:
                    raise SimulationError(
                        f"Simulation crashed at node {event.target} while processing "
                        f"'{event.name}': {error}"
                    ) from error

                # Snapshot the node's internal state AFTER processing
                if self.simulator.requires_state_snapshot:
                    raw_state = process.model.get_state() if process.model else {}
                    state = copy.deepcopy(raw_state)
                else:
                    state = {}

                for plugin in self.simulator._plugins:
                    plugin.on_event_processed(event, state, self.simulator)

                processed_events += 1

        end_real_time = time.perf_counter()

        return {
            "simulated_time_elapsed": self.simulator.clock,
            "total_messages": processed_events,
            "execution_real_time_sec": round(end_real_time - start_real_time, 5),
            "scheduled_events": self.simulator.scheduled_events,
            "dropped_by_time_horizon": self.simulator.dropped_by_time_horizon,
            "dropped_by_plugins": self.simulator.dropped_by_plugins,
        }
