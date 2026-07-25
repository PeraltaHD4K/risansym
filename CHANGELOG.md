# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [1.0.0rc1] - 2026-07-25

### Added
- GitHub Actions CI matrix testing.
- Web component refactoring into smaller hooks and components.
- conftest.py for pytest.
- A generated, versioned JSON Schema and shared valid/invalid trace fixtures.
- Machine-readable trace truncation metadata.
- Strict documentation and shared-contract validation in CI.
- Separate dependency-audit and deterministic-benchmark CI jobs.
- Verified wheel/sdist builds with an isolated installed-package smoke test.
- A protected TestPyPI workflow for release-candidate validation.

### Fixed
- Fixed TraceCollector O(n) popping by moving to collections.deque.
- Fixed React anti-pattern when updating clock state.
- Hardened EventLoop with proper try-except error handling.
- SVG generation fixes and improvements.
- Trace persistence now uses atomic replacement and cleans temporary files on failure.
- Removed high-severity transitive web dependency advisories by updating Next
  and pinning patched Minimatch, PostCSS, and Sharp dependency paths.

### Changed
- Reduced the package-root API to the supported 1.0 surface.
- Removed the legacy `Model.id` alias in favor of `Model.node_id`.
- Internal model/process binding methods now use private names.
- Event payloads are validated as finite JSON data and copied on construction.
- Source distributions now contain only the package and required packaging
  metadata, excluding tests, benchmarks, scripts, and lockfiles.
- PyPI publication now promotes the exact artifact verified by the release
  workflow instead of rebuilding it in the protected publication job.

### Breaking
- Removed all 0.x compatibility aliases and deprecated entry points.
- Replaced implicit simulation lifecycle behavior with explicit states and
  structured `SimulationResult` termination data.
- Made topology direction, event validation, plugin failure policy, and trace
  schema contracts explicit.
- Prevented completed simulations from being run again.
