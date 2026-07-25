# Contributing to Risansym

Thank you for helping improve Risansym. Contributions to the simulation core,
documentation, trace contract, and optional visualizer are welcome.

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
Security reports must follow [SECURITY.md](SECURITY.md), not the public issue
tracker.

## Before opening an issue

- Follow [SUPPORT.md](SUPPORT.md) for usage questions.
- Search existing issues before reporting a bug or proposing a feature.
- Include a minimal reproducible example for behavior involving the Python API.
- Describe changes to the trace schema explicitly because it is a shared
  Python/TypeScript contract.

## Development setup

Required tools:

- Python 3.10 or newer;
- [uv](https://docs.astral.sh/uv/);
- Node.js 24 or newer for visualizer changes.

Prepare the Python environment:

```bash
cd core
uv sync --all-groups
```

Prepare the visualizer:

```bash
cd web
npm ci
```

## Branch and pull-request workflow

1. Create a focused branch from an up-to-date `main`.
2. Keep each pull request limited to one coherent delivery.
3. Add or update tests and documentation with behavioral changes.
4. Add user-visible changes to the `Unreleased` section of `CHANGELOG.md`.
5. Run the relevant local gates.
6. Push the branch and open a pull request using the repository template.
7. Merge only after required CI checks and review are complete.

Do not commit directly to `main`. Releases and version changes are performed by
maintainers through the documented [release process](docs/releasing.md).

## Python quality gates

Run these commands from `core/`:

```bash
uv sync --all-groups
uv lock --check
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run mypy .
uv run pytest
```

Benchmarks are intentionally separate from functional tests:

```bash
uv run pytest benchmarks -m benchmark
```

Changes that intentionally affect performance should document the workload,
Python version, platform, commit, parameters, and comparison result.

## Documentation and shared-contract gates

Run the documentation build from the repository root:

```bash
uv run --project core mkdocs build --strict
```

When changing Pydantic trace models, regenerate and validate the checked-in
schema and update both valid and invalid shared fixtures:

```bash
cd core
uv run python scripts/generate_trace_schema.py
```

The Python model is the source of truth. Breaking trace changes require a new
`schema_version`.

## Visualizer gates

For changes under `web/` or `shared/`, run from `web/`:

```bash
npm ci
npm test
npm run lint
npm run build
```

Core-only changes do not normally require local frontend checks unless they
alter the shared trace contract.

## Public API and compatibility

The supported API is exported from `risansym`, `risansym.plugins`, and the
advanced `risansym.schemas` trace contract. Modules described as internal in
the architecture documentation may change without compatibility guarantees.

After 1.0.0, incompatible changes to supported APIs belong in a new major
version. Prefer additive, typed changes within the 1.x series. Never add a
compatibility alias without documenting its lifecycle.

## Style

- Follow the repository's Ruff formatting and lint configuration.
- Keep public APIs typed and documented.
- Prefer domain-specific exceptions and explicit result values.
- Keep simulation behavior deterministic when a seed or explicit random
  generator is supplied.
- Add focused tests for success, failure, and boundary cases.
