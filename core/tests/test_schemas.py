"""Tests for the Pydantic schema models."""

import json
import pytest
from risansym.schemas import (
    TransmitEvent,
    ReceiveEvent,
    AppLogEvent,
    TraceMetadata,
    TraceOutput,
)


class TestTransmitEvent:
    def test_valid_transmit_event(self):
        e = TransmitEvent(clock=1.0, event_time=2.0, source=1, target=2, name="MSG", payload={"data": 1})
        assert e.action == "TRANSMIT"
        assert e.clock == 1.0
        assert e.node_state is None

    def test_transmit_with_node_state(self):
        e = TransmitEvent(clock=1.0, event_time=2.0, source=1, target=2, name="MSG", payload={}, node_state={"leader": True})
        assert e.node_state == {"leader": True}

    def test_transmit_serialization_roundtrip(self):
        e = TransmitEvent(clock=1.0, event_time=2.0, source=1, target=2, name="MSG", payload={"x": 42})
        data = json.loads(e.model_dump_json())
        assert data["action"] == "TRANSMIT"
        assert data["payload"] == {"x": 42}


class TestReceiveEvent:
    def test_valid_receive_event(self):
        e = ReceiveEvent(clock=2.0, source=1, target=2, name="MSG", payload={})
        assert e.action == "RECEIVE"

    def test_receive_with_node_state(self):
        e = ReceiveEvent(clock=2.0, source=1, target=2, name="MSG", payload={}, node_state={"term": 3})
        assert e.node_state["term"] == 3


class TestAppLogEvent:
    def test_valid_app_log_event(self):
        e = AppLogEvent(clock=1.5, source=1, message="Hello world")
        assert e.action == "APP_LOG"
        assert e.message == "Hello world"


class TestTraceOutput:
    def test_full_trace_output_serialization(self):
        metadata = TraceMetadata(
            algorithm="TestAlgo",
            topology="ring",
            execution_date="20260704",
            parameters={"max_time": 10.0, "total_nodes": 3, "total_edges": 6},
            metrics={"total_messages": 5},
        )
        trace = [
            TransmitEvent(clock=0.0, event_time=1.0, source=1, target=2, name="PING", payload={}),
            ReceiveEvent(clock=1.0, source=1, target=2, name="PING", payload={}),
            AppLogEvent(clock=1.0, source=2, message="Got PING"),
        ]
        output = TraceOutput(metadata=metadata, trace=trace)

        # Roundtrip: serialize to JSON and parse back
        raw = output.model_dump_json(indent=2)
        parsed = TraceOutput.model_validate_json(raw)

        assert len(parsed.trace) == 3
        assert parsed.metadata.algorithm == "TestAlgo"
        assert parsed.trace[0].action == "TRANSMIT"
        assert parsed.trace[1].action == "RECEIVE"
        assert parsed.trace[2].action == "APP_LOG"
