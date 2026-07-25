# Risansym benchmarks

Performance benchmarks are intentionally separate from the functional test
suite.

Run them from `core/`:

```bash
uv run pytest benchmarks -m benchmark
```

Every benchmark must use deterministic input and record the Python version,
platform, commit, parameters, and result when establishing a release baseline.

The first persisted baseline for the 1.0 work will be recorded after the
correctness changes in phases 1 and 2 have stabilized.

## Entrega A baseline

The `baseline-0.9.0-*.json` files were measured with deterministic seed 42 on
Python 3.12.13. They are split by workload so long-running cases cannot prevent
smaller valid results from being persisted.

Approximate mean on the baseline machine:

- 1,000 nodes, probability 0.01: 0.154 seconds.
- 5,000 nodes, probability 0.002: 3.398 seconds.
- 10,000 nodes, probability 0.001: 12.938 seconds.

Compare JSON results only on equivalent hardware and runtime configuration.
