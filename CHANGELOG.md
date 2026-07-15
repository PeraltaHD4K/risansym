# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- GitHub Actions CI matrix testing.
- Web component refactoring into smaller hooks and components.
- conftest.py for pytest.

### Fixed
- Fixed TraceCollector O(n) popping by moving to collections.deque.
- Fixed React anti-pattern when updating clock state.
- Hardened EventLoop with proper try-except error handling.
- SVG generation fixes and improvements.
