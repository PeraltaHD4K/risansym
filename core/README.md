# Risansym (Core Engine)

Risansym is a powerful, Python-based discrete event simulator for distributed systems. It was designed to run complex network algorithms (such as Chandy-Lamport, logical clocks, token rings, etc.) and generate trace files that can be rendered using the Risansym Web Visualizer.

## Installation

```bash
pip install risansym
```

## Quick Start

```python
from risansym.simulation import Simulation

# Initialize with a topology file (e.g. edge list or adjacency matrix)
sim = Simulation.from_file("topology.txt", maxtime=10.0, trace_enabled=True)

# Run the simulation
sim.initialize_all()
sim.run()
```

## Official Documentation

For complete API reference, examples, and instructions on how to use the web visualizer, visit:
**[https://peraltahd4k.github.io/risansym/](https://peraltahd4k.github.io/risansym/)**
