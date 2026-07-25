# Release process

Risansym releases are built from an approved commit on `main`. The project uses
PyPI trusted publishing, protected GitHub environments, immutable tags, and
verified artifacts.

## One-time repository configuration

The repository owner must configure two GitHub environments:

- `testpypi`, with required reviewers and a matching TestPyPI trusted publisher.
- `pypi`, with required reviewers and a matching PyPI trusted publisher.

Both publishers must target this repository and their corresponding workflow
files. No long-lived package index token is required.

## Release candidate

1. Merge the release-preparation Pull Request after all required CI jobs pass.
2. Confirm the package version and changelog on `main`.
3. Run **Publish release candidate to TestPyPI** manually using the immutable
   commit SHA or tag as `ref`.
4. Approve the protected `testpypi` environment.
5. Install the candidate from TestPyPI in a clean environment and exercise the
   public quick-start example.
6. Record any blocker and fix it through a new branch and Pull Request.

The TestPyPI workflow builds the wheel and sdist once, validates archive paths,
metadata and `py.typed`, smoke-tests the installed wheel, and passes that exact
artifact to the protected publication job.

## PyPI release

1. Verify the latest `main` CI run is green.
2. Create an annotated `v`-prefixed tag whose value exactly matches
   `project.version`.
3. Push the tag and create a GitHub Release with the approved notes.
4. Approve the protected `pypi` environment.
5. Wait for **Publish to PyPI** to complete.
6. Install the published version from PyPI in a new environment and repeat the
   smoke test.

The publication workflow rejects a GitHub Release when its tag differs from the
package version. Its build job verifies and smoke-tests the artifacts; the
publication job downloads those same artifacts and cannot modify them.

## Local release gates

From `core/`:

```bash
uv sync --all-groups
uv lock --check
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run mypy .
uv run pytest
uv run pytest benchmarks -m benchmark
uv build
uv run python scripts/verify_distribution.py dist
```

From `web/`:

```bash
npm ci
npm audit --audit-level=high
npm test
npm run lint
npm run build
```

From the repository root:

```bash
uv run --project core mkdocs build --strict
```
