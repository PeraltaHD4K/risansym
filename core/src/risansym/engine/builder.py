from __future__ import annotations

import warnings
from pathlib import Path

from risansym.process import Process
from risansym.simulator import Simulator
from risansym.topology import load_adjacency_matrix


class SimulationBuilder:
    """Handles the construction of the simulation graph and components."""
    
    @staticmethod
    def build_topology(graph_input: list[list[int]] | str | Path) -> tuple[list[list[int]], str]:
        """Load or pass through the topology graph and determine its name."""
        if isinstance(graph_input, (str, Path)):
            warnings.warn(
                "Passing a filename directly to Simulation() is deprecated "
                "and will be removed in v1.0. Use Simulation.from_file() instead.",
                DeprecationWarning,
                stacklevel=3,
            )
            graph = load_adjacency_matrix(graph_input)
            topology_name = Path(graph_input).stem
        else:
            graph = graph_input
            topology_name = "unknown_topology"
            
        return graph, topology_name
        
    @staticmethod
    def build_processes(graph: list[list[int]], engine: Simulator) -> list[Process | None]:
        """Construct the process table based on the topology graph."""
        # Index 0 reserved as None; nodes are 1-indexed
        return [None] + [
            Process(row, engine, i)
            for i, row in enumerate(graph, start=1)
        ]
