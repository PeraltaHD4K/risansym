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
from risansym.topology import load_adjacency_matrix

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
    "Simulator",
    "TraceCollector",
    "TraceEvent",
    "TransmitEvent",
    "ReceiveEvent",
    "AppLogEvent",
    "TraceMetadata",
    "TraceOutput",
    "load_adjacency_matrix",
    "__version__",
]
