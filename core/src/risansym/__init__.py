"""Risansym's stable public API for discrete-event simulations."""

import logging
from importlib.metadata import PackageNotFoundError, version

from risansym.event import Event, JsonPayload, JsonValue
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
from risansym.model import Model
from risansym.plugins.base import EngineContext, SimulationContext, SimulationPlugin
from risansym.plugins.manager import PluginFailurePolicy
from risansym.results import (
    ScheduleResult,
    SimulationResult,
    SimulationState,
    TerminationReason,
)
from risansym.simulation import Simulation
from risansym.topology import (
    AdjacencyList,
    TopologyGenerator,
    load_adjacency_list,
    load_dense_matrix,
    load_edge_list,
    normalize_topology,
)

try:
    __version__ = version("risansym")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = [
    "AdjacencyList",
    "CausalityError",
    "ConfigurationError",
    "EngineContext",
    "Event",
    "InvalidEventError",
    "JsonPayload",
    "JsonValue",
    "Model",
    "PluginError",
    "PluginFailurePolicy",
    "RisansymError",
    "ScheduleResult",
    "Simulation",
    "SimulationContext",
    "SimulationError",
    "SimulationLimitReached",
    "SimulationPlugin",
    "SimulationResult",
    "SimulationState",
    "TerminationReason",
    "TopologyError",
    "TopologyGenerator",
    "TraceExportError",
    "__version__",
    "load_adjacency_list",
    "load_dense_matrix",
    "load_edge_list",
    "normalize_topology",
]
