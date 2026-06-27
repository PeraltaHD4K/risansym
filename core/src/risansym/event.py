from dataclasses import dataclass, field


@dataclass(order=True, slots=True)
class Event:
    """Encapsula la información que se intercambia entre procesos activos."""

    time: float
    # field(compare=False) evita desempates por nombre/IDs si los tiempos son iguales
    name: str = field(compare=False)
    target: int = field(compare=False)
    source: int = field(compare=False)
    payload: dict = field(default_factory=dict, compare=False)
  
