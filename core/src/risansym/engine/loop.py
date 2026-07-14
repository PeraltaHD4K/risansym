from __future__ import annotations

import time
from typing import Any

from risansym.process import Process
from risansym.schemas import ReceiveEvent
from risansym.simulator import Simulator
from risansym.trace import TraceCollector


class EventLoop:
    """Executes the simulation event loop and routes messages."""
    
    def __init__(
        self,
        simulator: Simulator,
        table: list[Process | None],
        collector: TraceCollector | None,
    ) -> None:
        self.simulator = simulator
        self.table = table
        self.collector = collector
        
    def run(self) -> dict[str, Any]:
        """Main loop: pop and route events until the agenda is empty.
        
        Returns:
            Dictionary containing execution metrics.
        """
        start_real_time = time.perf_counter()

        while self.simulator.is_on:
            event = self.simulator.pop_event()

            if event.target < 1 or event.target >= len(self.table):
                raise ValueError(
                    f"Event targets node {event.target}, but only nodes "
                    f"1-{len(self.table) - 1} exist in the topology."
                )

            if process := self.table[event.target]:
                process.set_time(event.time)
                process.receive(event)

                # Snapshot the node's internal state AFTER processing
                state = process.model.get_state() if process.model else {}

                if self.collector:
                    self.collector.record(ReceiveEvent(
                        action="RECEIVE",
                        clock=event.time,
                        source=event.source,
                        target=event.target,
                        name=event.name,
                        payload=event.payload,
                        node_state=state
                    ))

        end_real_time = time.perf_counter()

        return {
            "simulated_time_elapsed": self.simulator.clock,
            "total_messages": len(self.collector) if self.collector else 0,
            "execution_real_time_sec": round(end_real_time - start_real_time, 5)
        }
