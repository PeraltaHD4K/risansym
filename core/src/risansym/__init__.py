"""
Risansym — A Discrete Event Simulator for Distributed Systems.

Usage::

    from risansym import Simulation, Model, Event

    class MyAlgorithm(Model):
        def init(self):
            ...
        def receive(self, event):
            ...
"""

from risansym.simulation import Simulation
from risansym.model import Model
from risansym.process import Process
from risansym.event import Event, JsonPayload
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
from risansym.results import ScheduleResult
from risansym.simulator import Simulator
from risansym.trace import TraceCollector
from risansym.schemas import (
    TraceEvent,
    TransmitEvent,
    ReceiveEvent,
    AppLogEvent,
    TraceMetadata,
    TraceOutput,
)
from risansym.topology import (
    AdjacencyList,
    TopologyGenerator,
    load_adjacency_list,
    load_dense_matrix,
    load_edge_list,
    normalize_topology,
)

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("risansym")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

__all__ = [
    "Simulation",
    "Model",
    "Process",
    "Event",
    "JsonPayload",
    "ScheduleResult",
    "RisansymError",
    "ConfigurationError",
    "TopologyError",
    "SimulationError",
    "CausalityError",
    "InvalidEventError",
    "SimulationLimitReached",
    "PluginError",
    "TraceExportError",
    "Simulator",
    "TraceCollector",
    "TraceEvent",
    "TransmitEvent",
    "ReceiveEvent",
    "AppLogEvent",
    "TraceMetadata",
    "TraceOutput",
    "AdjacencyList",
    "normalize_topology",
    "load_adjacency_list",
    "load_edge_list",
    "load_dense_matrix",
    "TopologyGenerator",
    "__version__",
]
