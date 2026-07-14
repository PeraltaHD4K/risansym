"""Tests for the Event dataclass."""

from risansym.event import Event, JsonPayload


class TestEventOrdering:
    """Verify that events are ordered solely by time."""

    def test_earlier_event_is_smaller(self):
        e1 = Event(time=1.0, source=1, target=2, name="A")
        e2 = Event(time=2.0, source=1, target=2, name="B")
        assert e1 < e2

    def test_same_time_events_are_equal(self):
        e1 = Event(time=1.0, source=1, target=2, name="X")
        e2 = Event(time=1.0, source=3, target=4, name="Y")
        # compare=False fields should not affect ordering
        assert not (e1 < e2) and not (e2 < e1)

    def test_sorting_list_of_events(self):
        events = [
            Event(time=3.0, source=1, target=2, name="C"),
            Event(time=1.0, source=1, target=2, name="A"),
            Event(time=2.0, source=1, target=2, name="B"),
        ]
        sorted_events = sorted(events)
        assert [e.time for e in sorted_events] == [1.0, 2.0, 3.0]


class TestEventPayload:
    """Verify payload typing and defaults."""

    def test_default_payload_is_empty_dict(self):
        e = Event(time=0.0, source=1, target=2, name="TEST")
        assert e.payload == {}

    def test_payload_accepts_typed_dict(self):
        payload: JsonPayload = {"key": "value", "count": 42}
        e = Event(time=0.0, source=1, target=2, name="TEST", payload=payload)
        assert e.payload["key"] == "value"

    def test_separate_instances_have_independent_payloads(self):
        """Ensure default_factory creates separate dicts per instance."""
        e1 = Event(time=0.0, source=1, target=2, name="A")
        e2 = Event(time=0.0, source=1, target=2, name="B")
        e1.payload["x"] = 1
        assert "x" not in e2.payload


class TestEventValidation:
    """Verify Event construction validation and argument order."""

    def test_event_positional_args(self):
        # T1: positional args order is (time, name, source, target)
        e = Event(1.0, "MSG", 1, 2)
        assert e.time == 1.0
        assert e.name == "MSG"
        assert e.source == 1
        assert e.target == 2

    def test_event_invalid_time(self):
        import pytest
        import math
        # T2: NaN and inf times raise ValueError
        with pytest.raises(ValueError, match="Invalid event time"):
            Event(time=math.nan, source=1, target=2, name="MSG")
        with pytest.raises(ValueError, match="Invalid event time"):
            Event(time=math.inf, source=1, target=2, name="MSG")
        with pytest.raises(ValueError, match="Invalid event time"):
            Event(time=-1.0, source=1, target=2, name="MSG")
