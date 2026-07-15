# Contributing to Risansym

First off, thanks for taking the time to contribute!

## Development Setup

1. Fork the repo and clone it locally.
2. Install [uv](https://github.com/astral-sh/uv) and Node.js 24+.
3. For the Python core engine, run `uv sync` in the `core/` directory.
4. For the web dashboard, run `npm install` in the `web/` directory.

## Pull Request Process

1. Ensure all tests pass (`uv run pytest` and `npm test`).
2. Run linters (`uv run ruff check .` and `npm run lint`).
3. Create a branch, push, and open a PR!
