"""Tests for the public Risansym exception hierarchy."""

from risansym.exceptions import (
    CausalityError,
    ConfigurationError,
    InvalidEventError,
    PluginError,
    RisansymError,
    SimulationError,
    SimulationLimitReached,
    TopologyError,
    TraceExportError,
)


def test_all_domain_exceptions_inherit_from_risansym_error() -> None:
    exception_types = (
        ConfigurationError,
        TopologyError,
        SimulationError,
        CausalityError,
        InvalidEventError,
        SimulationLimitReached,
        PluginError,
        TraceExportError,
    )

    assert all(issubclass(exception_type, RisansymError) for exception_type in exception_types)


def test_configuration_and_topology_errors_are_value_errors() -> None:
    assert issubclass(ConfigurationError, ValueError)
    assert issubclass(TopologyError, ValueError)


def test_simulation_errors_are_runtime_errors() -> None:
    assert issubclass(SimulationError, RuntimeError)
    assert issubclass(CausalityError, SimulationError)
    assert issubclass(InvalidEventError, SimulationError)
