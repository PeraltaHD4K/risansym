# Getting Started

This guide installs Risansym and runs a complete two-node simulation.

## Prerequisites

- Python 3.10 or newer.
- `pip` or, optionally, [uv](https://docs.astral.sh/uv/).

## Installation

```bash
pip install risansym
```

With uv:

```bash
uv add risansym
```

Confirm which package the interpreter imports:

```bash
python -c "import risansym; print(risansym.__version__, risansym.__file__)"
```

## First simulation

Create `first_simulation.py`:

```python
from risansym import Event, Model, Simulation, TopologyGenerator


class Receiver(Model):
    def init(self) -> None:
        pass

    def receive(self, event: Event) -> None:
        print(f"node {self.node_id} received {event.name} at t={self.clock}")


graph = TopologyGenerator.line(2)
simulation = Simulation(graph, maxtime=10.0)

simulation.set_model(Receiver(), 1)
simulation.set_model(Receiver(), 2)
simulation.initialize_all()
simulation.seed_event(
    Event(time=1.0, name="HELLO", source=1, target=2),
)

result = simulation.run()
assert result.complete
print(result)
```

Run it:

```bash
python first_simulation.py
```

Node identifiers are one-based. Every topology row contains the direct
neighbors of that node.

## Add observability

Plugins are optional. Attach them before `initialize_all()`:

```python
from risansym.plugins import ConsoleLoggerPlugin, JSONTracerPlugin

simulation.attach(ConsoleLoggerPlugin(trace_network=True, app_logs=True))
simulation.attach(
    JSONTracerPlugin(
        "Receiver",
        trace_dir="traces",
        trace_tag="first-run",
    )
)
```

The console plugin prints selected events. The tracer writes a versioned JSON
document after the simulation completes. See [Plugins](plugins.md) for
configuration and custom extensions.

## Load a topology file

`Simulation.from_file()` accepts adjacency lists, edge lists, and dense
matrices. An adjacency-list file named `graph.txt` could contain:

```text
# Node 1 is connected to node 2.
2
1
```

Load it with:

```python
simulation = Simulation.from_file(
    "graph.txt",
    maxtime=10.0,
    format="adjacency_list",
)
```

For generated graphs, directed graphs, all file formats, and export, continue
with [Creating Topologies](topologies.md). To implement a protocol, continue
with [Writing Algorithms](writing_algorithms.md).
