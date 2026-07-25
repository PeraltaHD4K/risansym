# Getting Started

Learn how to install Risansym and set up your first simulation.

## Prerequisites

- Python 3.10 or higher.
- (Optional but recommended) `uv` for lightning-fast package management.

## Installation

Install the simulation core directly from PyPI:

```bash
uv add risansym
# or using pip
pip install risansym
```

## Creating a Topology

Risansym represents network topologies using standard adjacency-list text files. Create a file named `graph.txt`:

```text
# Each row represents one node and lists its one-based neighbors.
2
1 3
2
```

## Running the Simulation

You can instantiate the simulator by passing your topology file.

```python
from risansym import Simulation
from risansym.plugins import JSONTracerPlugin

# Create the simulation engine
engine = Simulation.from_file(
    filename="graph.txt",
    maxtime=100.0,
)
engine.attach(JSONTracerPlugin("MyFirstAlgorithm", trace_dir="traces"))

# Initialize all models (we haven't attached any yet!)
engine.initialize_all()

# Run the simulation loop
result = engine.run()
assert result.complete
```

`Simulation` only receives execution concerns. Observability is explicit:
attach `JSONTracerPlugin` to record events and node states, and pass
`trace_path` to that plugin when you need a fixed output file.

Proceed to [Writing Algorithms](writing_algorithms.md) to learn how to inject behavior into your nodes.
