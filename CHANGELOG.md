# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- GitHub Actions CI matrix testing.
- Web component refactoring into smaller hooks and components.
- conftest.py for pytest.
- A generated, versioned JSON Schema and shared valid/invalid trace fixtures.
- Machine-readable trace truncation metadata.

### Fixed
- Fixed TraceCollector O(n) popping by moving to collections.deque.
- Fixed React anti-pattern when updating clock state.
- Hardened EventLoop with proper try-except error handling.
- SVG generation fixes and improvements.
- Trace persistence now uses atomic replacement and cleans temporary files on failure.

### Changed
- Reduced the package-root API to the supported 1.0 surface.
- Removed the legacy `Model.id` alias in favor of `Model.node_id`.
- Internal model/process binding methods now use private names.
- Event payloads are validated as finite JSON data and copied on construction.
