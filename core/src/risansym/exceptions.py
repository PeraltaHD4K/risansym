"""Public exception hierarchy for Risansym."""


class RisansymError(Exception):
    """Base class for all Risansym domain errors."""


class ConfigurationError(RisansymError, ValueError):
    """Raised when simulation configuration is invalid."""


class TopologyError(RisansymError, ValueError):
    """Raised when a topology is malformed or violates its declared semantics."""


class SimulationError(RisansymError, RuntimeError):
    """Base class for errors raised while executing a simulation."""


class CausalityError(SimulationError):
    """Raised when an event would move simulated time backwards."""


class InvalidEventError(SimulationError, ValueError):
    """Raised when an event violates the engine contract."""


class SimulationLimitReached(SimulationError):
    """Raised when a configured simulation resource limit is reached."""


class PluginError(SimulationError):
    """Raised when a plugin violates its contract or fails."""


class TraceExportError(RisansymError):
    """Raised when a simulation trace cannot be persisted."""
