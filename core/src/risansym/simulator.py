import heapq
from typing import TYPE_CHECKING

from risansym.event import Event
from risansym.schemas import TransmitEvent, ReceiveEvent, AppLogEvent

if TYPE_CHECKING:
    from risansym.trace import TraceCollector


class Simulator:
    """Motor de simulación dirigido por eventos, coordinado por heap de mínimos."""

    def __init__(self, maxtime: float, debug: bool = True, collector: 'TraceCollector | None' = None) -> None:
        self.clock: float = 0.0
        self.maxtime: float = maxtime
        self._agenda: list[Event] = []
        self.debug: bool = debug
        self._collector = collector

    def insert_event(self, event: Event, node_state: dict | None = None) -> None:
        """Inserta un evento en el heap si está dentro del horizonte temporal."""
        if event.time <= self.maxtime:
            heapq.heappush(self._agenda, event)
            if self.debug:
                print(f"[t={self.clock:.1f}] Nodo {event.source} TRANSMITE '{event.name}' -> Nodo {event.target} (llegará en t={event.time:.1f})")
            
            if self._collector:
                self._collector.record(TransmitEvent(
                    action="TRANSMIT",
                    clock=self.clock,
                    event_time=event.time,
                    source=event.source,
                    target=event.target,
                    name=event.name,
                    payload=event.payload,
                    node_state=node_state
                ))

    def pop_event(self) -> Event:
        """Extrae el evento más próximo y avanza el reloj global."""
        event = heapq.heappop(self._agenda)
        self.clock = event.time
        if self.debug:
            print(f"[t={self.clock:.1f}] Nodo {event.target} RECIBE '{event.name}' <- Nodo {event.source}")
            
        # Nota: La grabación en el TraceCollector de ReceiveEvent ahora se hace desde
        # Simulation._execute() para poder capturar el estado del nodo DESPUÉS de procesarlo.
        return event

    def log_app_event(self, source: int, message: str) -> None:
        """Registra un evento lógico de aplicación en la traza."""
        if self.debug:
            print(f"[t={self.clock:.1f}] APP Nodo {source}: {message}")
            
        if self._collector:
            self._collector.record(AppLogEvent(
                action="APP_LOG",
                clock=self.clock,
                source=source,
                message=message
            ))

    @property
    def is_on(self) -> bool:
        """True mientras existan eventos pendientes en la agenda."""
        return bool(self._agenda)
