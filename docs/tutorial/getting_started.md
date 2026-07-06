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
# node: neighbors
1: 2
2: 1 3
3: 2
```

## Running the Simulation

You can instantiate the simulator by passing your topology file.

```python
from risansym import Simulation

# Create the simulation engine
engine = Simulation.from_file(
    filename="graph.txt",
    maxtime=100.0,
    algo_name="MyFirstAlgorithm",
    debug=True,
    trace=True
)

# Initialize all models (we haven't attached any yet!)
engine.initialize_all()

# Run the simulation loop
engine.run()
```

If `trace=True` is set, Risansym will automatically generate a detailed JSON file in the `traces/` folder when the simulation finishes. This file can be uploaded to the Web Visualizer.

Proceed to [Writing Algorithms](writing_algorithms.md) to learn how to inject behavior into your nodes.
