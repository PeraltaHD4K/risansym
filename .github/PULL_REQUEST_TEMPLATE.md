## Summary

<!-- What problem does this PR solve and what is the resulting behavior? -->

## Related issue

<!-- Use "Closes #123" when appropriate. -->

## Scope

- [ ] Python core or public API
- [ ] Tests or benchmarks
- [ ] Documentation
- [ ] Shared trace contract
- [ ] Web visualizer
- [ ] Packaging or release automation

## Validation

<!-- List commands actually run and their results. Remove irrelevant lines. -->

- [ ] `uv run ruff check .`
- [ ] `uv run ruff format --check .`
- [ ] `uv run mypy src`
- [ ] `uv run mypy .`
- [ ] `uv run pytest`
- [ ] `uv run pytest benchmarks -m benchmark`
- [ ] `uv run --project core mkdocs build --strict`
- [ ] `npm test`
- [ ] `npm run lint`
- [ ] `npm run build`

## Contract review

- [ ] Tests cover changed behavior and relevant failure paths.
- [ ] User-facing behavior is documented.
- [ ] `CHANGELOG.md` is updated when users are affected.
- [ ] Public API compatibility has been considered.
- [ ] Trace schema and shared fixtures are updated together, or are unaffected.
- [ ] Performance and reproducibility effects have been considered.

## Reviewer notes

<!-- Call out migration steps, deliberate tradeoffs, or areas needing special review. -->
