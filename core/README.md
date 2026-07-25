# Risansym (Core Engine)

Risansym is a powerful, Python-based discrete event simulator for distributed systems. It was designed to run complex network algorithms (such as Chandy-Lamport, logical clocks, token rings, etc.) and generate trace files that can be rendered using the Risansym Web Visualizer.

## Installation

```bash
pip install risansym
```

## Quick Start

```python
from risansym import Event, Model, ScheduleResult, Simulation
from risansym.plugins import JSONTracerPlugin


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
)
sim.attach(JSONTracerPlugin("Ping", trace_dir="traces"))

sim.set_model(Ping(), 1)
sim.set_model(Ping(), 2)
sim.initialize_all()
result = sim.seed_event(
    Event(time=0.0, name="PING", source=1, target=2),
)
assert result is ScheduleResult.SCHEDULED
simulation_result = sim.run()
assert simulation_result.complete
```

## Lifecycle and incremental execution

A simulation moves through `CREATED`, `INITIALIZING`, `READY`, `RUNNING`,
`STOPPED`, `COMPLETED`, or `FAILED`. Models and plugins can only be configured
while it is `CREATED`. Initialization is transactional: a model failure leaves
the simulation in `FAILED` and removes events scheduled by earlier model
initializers.

`run()`, `step()`, and `run_until(time)` return an immutable
`SimulationResult`. Event-budget and time-boundary results remain in `STOPPED`
and can continue later; a `COMPLETED` simulation cannot run again.

```python
partial = sim.run(max_events=100)
if not partial.complete:
    final = sim.run()
```

## Plugins

Plugins subclass `SimulationPlugin` and receive immutable
`SimulationContext` or `EngineContext` values. They run in registration order.
Failures use an explicit `PluginFailurePolicy`: `RAISE`, `LOG`, or `DISABLE`.
The default is `RAISE`; trace export errors are therefore visible to callers.
State snapshots are copied only when an enabled plugin requests them.

## Public API and trace contract

The package root exposes the stable 1.0 simulation API. Trace models and
built-in plugins are advanced APIs under `risansym.schemas` and
`risansym.plugins`. Engine, process, runtime, exporter, plugin-manager, and
collector modules are implementation details.

Event payloads and model snapshots must contain JSON values. Payload input is
deep-copied when an event is created and should be treated as read-only.
Traces are written atomically and include `metadata.capture`, which identifies
retention limits and any discarded events.

## Topology contract

Risansym uses a validated adjacency list with one-based node identifiers.
An empty row represents an isolated node. Duplicate neighbors and self-loops
are rejected. Undirected topologies must contain every edge in both
directions; asymmetric adjacency is accepted only with `directed=True`.

Topologies can be loaded with `load_adjacency_list`, `load_edge_list`, or
`load_dense_matrix`. An edge-list file can preserve isolated nodes by passing
`node_count`. Deterministic generators accept a `seed` or an explicit
`random.Random` instance.

`Model.transmit(event)` enforces these topology edges: `event.source` must be
the sending model's `node_id`, and `event.target` must be either that same node
or one of its direct neighbors. Algorithms must route messages to non-neighbor
destinations through intermediate nodes. A spoofed source or non-neighbor
target raises `InvalidEventError`.

## Errors and scheduling outcomes

All domain errors derive from `RisansymError`. Consumers can catch narrower
errors such as `ConfigurationError`, `TopologyError`, `CausalityError`,
`InvalidEventError`, `PluginError`, and `TraceExportError`.

Invalid configuration and topology are reported with `ConfigurationError` and
`TopologyError`. Invalid event identity, routing, or shape raises
`InvalidEventError`; scheduling in the simulated past raises
`CausalityError`; and resource limits raise `SimulationLimitReached`. Plugin
callback failures use `PluginError`. A tracer reports a persistence failure as
its chained `TraceExportError` cause under the default `RAISE` policy. Failures
raised by a model's `init()` or `receive()` are chained inside
`SimulationError` with node and event context; the original exception remains
available as `error.__cause__`.

Expected scheduling decisions are values, not exceptions:

- `ScheduleResult.SCHEDULED` means the event entered the agenda.
- `ScheduleResult.DROPPED_TIME_HORIZON` means its time exceeded `maxtime`.
- `ScheduleResult.DROPPED_BY_PLUGIN` means a plugin deliberately discarded it.

`SimulationResult` reports the corresponding scheduled and dropped counters.

## Official Documentation

For complete API reference, examples, and instructions on how to use the web visualizer, visit:
**[https://peraltahd4k.github.io/risansym/docs](https://peraltahd4k.github.io/risansym/docs)**
