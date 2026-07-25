# Reproducibility and Performance

Discrete-event execution is deterministic when the same topology, models,
initial events, plugin behavior, and random inputs are used.

## Randomness

Risansym does not modify Python's module-level random state. Pass a seed or an
explicit `random.Random` instance to random topology generation:

```python
import random

from risansym import TopologyGenerator

topology = TopologyGenerator.random(1_000, 0.01, seed=42)
rng = random.Random(42)
```

Algorithm models should likewise own or receive their random-number generator
instead of depending on unrelated global random calls.

Record at least:

- Risansym and Python versions;
- topology parameters and seed;
- model configuration;
- seed events;
- plugin configuration and trace retention limits;
- operating system and hardware for performance comparisons.

## Event ordering

Events are ordered by simulated time and deterministic scheduler tie-breaking.
Do not infer distributed causality from wall-clock execution time.

## Trace retention

`JSONTracerPlugin(max_events=...)` bounds retained trace entries. Trace metadata
reports recorded and discarded entries. A truncated trace is valid but is not
a complete observation of the run.

## Snapshot cost

State snapshots are only captured when an enabled plugin requests them.
Tracing models with large mutable states can be expensive because snapshots
are deep-copied at scheduling and processing boundaries. Keep `get_state()`
focused on information required for analysis rather than returning every
internal object.

## Benchmarks

Functional tests and benchmarks are separate:

```bash
cd core
uv run pytest benchmarks -m benchmark
```

Benchmark comparisons are meaningful only with equivalent workloads, Python
versions, platforms, and runtime configurations. Checked-in baselines document
their seed and environment and are not universal performance guarantees.
