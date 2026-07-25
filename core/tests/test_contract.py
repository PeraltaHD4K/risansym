import json
from pathlib import Path
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
