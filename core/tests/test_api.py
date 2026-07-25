"""Tests for the public API exposed via __init__.py."""


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
        from risansym import TraceEvent, TransmitEvent

        assert TraceEvent is not None
        assert TransmitEvent is not None

    def test_import_json_payload(self):
        from risansym import JsonPayload

        assert JsonPayload is not None

    def test_import_domain_errors_and_schedule_result(self):
        from risansym import RisansymError, ScheduleResult, TopologyError

        assert RisansymError is not None
        assert TopologyError is not None
        assert ScheduleResult.SCHEDULED.value == "scheduled"

    def test_import_lifecycle_and_plugin_api(self):
        from risansym import (
            EngineContext,
            PluginFailurePolicy,
            PluginManager,
            SimulationContext,
            SimulationPlugin,
            SimulationResult,
            SimulationState,
            TerminationReason,
        )

        assert SimulationResult is not None
        assert SimulationState.CREATED.value == "created"
        assert TerminationReason.MAX_EVENTS.value == "max_events"
        assert SimulationPlugin is not None
        assert SimulationContext is not None
        assert EngineContext is not None
        assert PluginFailurePolicy.RAISE.value == "raise"
        assert PluginManager is not None

    def test_import_topology_api(self):
        from risansym import (
            AdjacencyList,
            load_adjacency_list,
            load_dense_matrix,
            load_edge_list,
            normalize_topology,
        )

        assert AdjacencyList is not None
        assert load_adjacency_list is not None
        assert load_dense_matrix is not None
        assert load_edge_list is not None
        assert normalize_topology is not None

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
