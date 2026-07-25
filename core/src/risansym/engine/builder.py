from __future__ import annotations

from collections.abc import Sequence

from risansym.process import Process
from risansym.simulator import Simulator
from risansym.topology import AdjacencyList, normalize_topology


class SimulationBuilder:
    """Handles the construction of the simulation graph and components."""

    @staticmethod
    def build_topology(
        graph: Sequence[Sequence[int]],
        *,
        directed: bool,
    ) -> tuple[AdjacencyList, str]:
        """Normalize a topology and assign its default name."""
        return normalize_topology(graph, directed=directed), "generated"

    @staticmethod
    def build_processes(graph: list[list[int]], engine: Simulator) -> list[Process | None]:
        """Construct the process table based on the topology graph."""
        # Index 0 reserved as None; nodes are 1-indexed
        return [None] + [Process(row, engine, i) for i, row in enumerate(graph, start=1)]
