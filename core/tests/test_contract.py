import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from risansym.schemas import TraceOutput


def test_shared_fixture_contract() -> None:
    """Validates that the Python Pydantic schema can parse the shared fixture."""
    fixture_path = Path(__file__).parent.parent.parent / "shared" / "fixtures" / "trace_valid.json"
    assert fixture_path.exists(), "Shared fixture not found"

    with fixture_path.open() as f:
        data = json.load(f)

    # If this fails, the Python schema has drifted from the shared contract
    parsed = TraceOutput.model_validate(data)
    assert parsed.metadata.algorithm == "PingPong"
    assert len(parsed.trace) == 3


@pytest.mark.parametrize(
    "fixture_name",
    [
        "trace_invalid_negative_time.json",
        "trace_invalid_truncation.json",
    ],
)
def test_invalid_shared_fixture_is_rejected(fixture_name: str) -> None:
    fixture_path = Path(__file__).parent.parent.parent / "shared" / "fixtures" / fixture_name
    with pytest.raises(ValidationError), fixture_path.open(encoding="utf-8") as fixture:
        TraceOutput.model_validate(json.load(fixture))


def test_checked_in_json_schema_is_current() -> None:
    schema_path = Path(__file__).parent.parent.parent / "shared" / "schema" / "trace.schema.json"
    assert json.loads(schema_path.read_text(encoding="utf-8")) == TraceOutput.model_json_schema()
