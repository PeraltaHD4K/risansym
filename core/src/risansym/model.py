from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from risansym.event import Event

if TYPE_CHECKING:
    from risansym.process import Process


class Model(ABC):
    """Interfaz abstracta (contrato) para los algoritmos distribuidos."""

    def __init__(self) -> None:
        self.clock: float = 0.0
        self.process: Process | None = None
        self.neighbors: list[int] = []
        self.id: int = 0

    def set_time(self, time: float) -> None:
        self.clock = time

    def set_process(self, process: Process, neighbors: list[int], node_id: int) -> None:
        self.process = process
        self.neighbors = neighbors
        self.id = node_id

    def transmit(self, event: Event) -> None:
        if self.process:
            self.process.transmit(event)

    def log(self, message: str) -> None:
        """Convención: Usar este método en lugar de print() para reportar eventos lógicos de la capa de aplicación."""
        if self.process:
            self.process.log(message)

    @abstractmethod
    def init(self) -> None:
        """Inicialización del estado local (implementado por la subclase)."""

    @abstractmethod
    def receive(self, event: Event) -> None:
        """Lógica de transición de la máquina de estados (implementado por subclase)."""
