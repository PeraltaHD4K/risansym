from __future__ import annotations

import warnings
from pathlib import Path

from risansym.process import Process
from risansym.simulator import Simulator
from risansym.topology import load_adjacency_matrix


class SimulationBuilder:
    """Handles the construction of the simulation graph and components."""
    
    @staticmethod
    def build_topology(graph: list[list[int]]) -> tuple[list[list[int]], str]:
        """Pass through the topology graph and assign a default name."""
        return graph, "unknown_topology"
        
    @staticmethod
    def build_processes(graph: list[list[int]], engine: Simulator) -> list[Process | None]:
        """Construct the process table based on the topology graph."""
        # Index 0 reserved as None; nodes are 1-indexed
        return [None] + [
            Process(row, engine, i)
            for i, row in enumerate(graph, start=1)
        ]
