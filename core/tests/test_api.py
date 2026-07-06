"""Tests for the public API exposed via __init__.py."""

import pytest


class TestPublicAPI:
    """Verify that all symbols are importable from the top-level package."""

    def test_import_simulation(self):
        from risansym import Simulation
        assert Simulation is not None

    def test_import_model(self):
        from risansym import Model
        assert Model is not None

    def test_import_event(self):
        from risansym import Event
        assert Event is not None

    def test_import_process(self):
        from risansym import Process
        assert Process is not None

    def test_import_simulator(self):
        from risansym import Simulator
        assert Simulator is not None

    def test_import_schema_types(self):
        from risansym import TraceEvent, TransmitEvent, ReceiveEvent, AppLogEvent
        from risansym import TraceMetadata, TraceOutput
        assert TraceEvent is not None
        assert TransmitEvent is not None

    def test_import_json_payload(self):
        from risansym import JsonPayload
        assert JsonPayload is not None

    def test_version_is_defined(self):
        import risansym
        import re
        assert hasattr(risansym, "__version__")
        assert isinstance(risansym.__version__, str)
        assert re.match(r"^\d+\.\d+\.\d+(-\w+)?$", risansym.__version__)

    def test_all_exports_match(self):
        import risansym
        for name in risansym.__all__:
            assert hasattr(risansym, name), f"{name} listed in __all__ but not importable"
