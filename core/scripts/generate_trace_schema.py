"""Generate the shared trace JSON Schema from the authoritative Pydantic model."""

from __future__ import annotations

import json
from pathlib import Path

from risansym.schemas import TraceOutput


def main() -> None:
    """Write the deterministic schema consumed by contract tests and the web app."""
    repository_root = Path(__file__).resolve().parents[2]
    destination = repository_root / "shared" / "schema" / "trace.schema.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(TraceOutput.model_json_schema(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
