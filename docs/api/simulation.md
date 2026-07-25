::: risansym.Simulation

## Lifecycle

`Simulation.state` follows a strict state machine:

`CREATED → INITIALIZING → READY → RUNNING → COMPLETED`

Limited execution returns to `STOPPED` and may continue. Any initialization,
model, plugin, or trace failure moves the simulation to `FAILED`. Configuration
methods such as `set_model()` and `attach()` are only valid in `CREATED`.

## Composition

`Simulation` contains only topology and execution configuration. Logging,
tracing, and future integrations are opt-in plugins:

```python
from risansym import Simulation
from risansym.plugins import ConsoleLoggerPlugin, JSONTracerPlugin

simulation = Simulation([[2], [1]], maxtime=10.0)
simulation.attach(ConsoleLoggerPlugin(app_logs=True))
simulation.attach(JSONTracerPlugin("MyAlgorithm", trace_dir="traces"))
```

Each plugin owns its own configuration. This keeps the simulation constructor
stable as new observability or integration features are added.

## Execution results

`run()`, `step()`, and `run_until()` return a `SimulationResult`. It records
the termination reason, simulated time, processed and pending events, dropped
events, and wall-clock duration. Check `result.complete` rather than inferring
completion from an empty return value.

```python
result = simulation.run(max_events=1_000)
if not result.complete:
    result = simulation.run()
```

`step()` processes at most one event. `run_until(time)` never processes an
event scheduled after the requested time.

## Plugin failures

Plugins run through a `PluginManager` and receive immutable contexts.
`PluginFailurePolicy.RAISE` propagates a `PluginError`, `LOG` records and
continues, and `DISABLE` records the first failure and disables that plugin.
