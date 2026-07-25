# Plugins

Plugins add observability or event-scheduling behavior without adding
configuration to the simulation engine.

Attach every plugin before `Simulation.initialize_all()`:

```python
from risansym.plugins import ConsoleLoggerPlugin, JSONTracerPlugin

simulation.attach(ConsoleLoggerPlugin(trace_network=True, app_logs=True))
simulation.attach(JSONTracerPlugin("MyAlgorithm", trace_dir="traces"))
```

Plugins run in registration order.

## Console logging

`ConsoleLoggerPlugin` can independently display network scheduling and
application logs:

```python
ConsoleLoggerPlugin(
    trace_network=True,
    app_logs=True,
)
```

Models should call `self.log("message")` for application logs. Plain `print()`
output is not part of a trace.

## JSON traces

`JSONTracerPlugin` owns the trace label, destination, optional tag, and event
retention limit:

```python
JSONTracerPlugin(
    "MyAlgorithm",
    trace_dir="traces",
    trace_tag="experiment-42",
    max_events=100_000,
)
```

Use `trace_path` instead of `trace_dir` when the output filename must be fixed.
A trace is written atomically when the simulation reaches a terminal state.
Persistence failures are visible to the caller under the default failure
policy.

State snapshots are requested only while an enabled plugin needs them. Large
states can make tracing expensive because snapshots are deep-copied at
transmission and processing boundaries.

## Failure policies

A plugin can use:

- `PluginFailurePolicy.RAISE`: fail the simulation, the default;
- `PluginFailurePolicy.LOG`: record the failure and continue;
- `PluginFailurePolicy.DISABLE`: record the first failure and disable that
  plugin.

```python
from risansym import PluginFailurePolicy

simulation.attach(
    optional_plugin,
    failure_policy=PluginFailurePolicy.DISABLE,
)
```

Use `RAISE` when missing output would invalidate an experiment.

## Custom plugin

Subclass `SimulationPlugin` and override only the callbacks you need:

```python
from risansym import EngineContext, Event, JsonPayload, SimulationPlugin


class EventCounter(SimulationPlugin):
    def __init__(self) -> None:
        self.scheduled = 0

    def on_event_schedule(
        self,
        event: Event,
        context: EngineContext,
        node_state: JsonPayload | None = None,
    ) -> Event | None:
        self.scheduled += 1
        return event
```

`on_event_schedule()` may return the event, replace it with another valid
event, or return `None` to drop it intentionally. Context objects are immutable
views. A plugin must not depend on modules documented as internal.
