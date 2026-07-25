# Risansym (Core Engine)

Risansym is a powerful, Python-based discrete event simulator for distributed systems. It was designed to run complex network algorithms (such as Chandy-Lamport, logical clocks, token rings, etc.) and generate trace files that can be rendered using the Risansym Web Visualizer.

## Installation

```bash
pip install risansym
```

## Quick Start

```python
from risansym import Event, Model, ScheduleResult
from risansym.simulation import Simulation


class Ping(Model):
    def init(self) -> None:
        pass

    def receive(self, event: Event) -> None:
        self.log(f"received {event.name}")


# Every row is a one-based node and contains its neighbors.
sim = Simulation(
    [[2], [1]],
    maxtime=10.0,
    directed=False,
    trace_enabled=True,
)

sim.set_model(Ping(), 1)
sim.set_model(Ping(), 2)
sim.initialize_all()
result = sim.seed_event(
    Event(time=0.0, name="PING", source=1, target=2),
)
assert result is ScheduleResult.SCHEDULED
sim.run()
```

## Topology contract

Risansym uses a validated adjacency list with one-based node identifiers.
An empty row represents an isolated node. Duplicate neighbors and self-loops
are rejected. Undirected topologies must contain every edge in both
directions; asymmetric adjacency is accepted only with `directed=True`.

Topologies can be loaded with `load_adjacency_list`, `load_edge_list`, or
`load_dense_matrix`. An edge-list file can preserve isolated nodes by passing
`node_count`. Deterministic generators accept a `seed` or an explicit
`random.Random` instance.

## Errors and scheduling outcomes

All domain errors derive from `RisansymError`. Consumers can catch narrower
errors such as `ConfigurationError`, `TopologyError`, `CausalityError`,
`InvalidEventError`, `PluginError`, and `TraceExportError`.

Scheduling an event returns `ScheduleResult.SCHEDULED`,
`ScheduleResult.DROPPED_TIME_HORIZON`, or
`ScheduleResult.DROPPED_BY_PLUGIN`. The simulator also exposes counters for
these outcomes, so rejected events are observable.

## Official Documentation

For complete API reference, examples, and instructions on how to use the web visualizer, visit:
**[https://peraltahd4k.github.io/risansym/docs](https://peraltahd4k.github.io/risansym/docs)**
