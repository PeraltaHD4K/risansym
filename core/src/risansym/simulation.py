from __future__ import annotations

import datetime
import time
from pathlib import Path

from risansym.event import Event
from risansym.model import Model
from risansym.process import Process
from risansym.simulator import Simulator
from risansym.schemas import TraceMetadata


class Simulation:
    """Orquestador global del grafo computacional y ciclo de simulación."""

    def __init__(self, filename: str | Path, maxtime: float, algo_name: str = "UnknownAlgo", debug: bool = True, trace: bool | str | Path = False, trace_dir: str = "traces", trace_tag: str | None = None) -> None:
        from risansym.trace import TraceCollector
        
        self.filename = Path(filename)
        self.algo_name = algo_name
        self.trace = trace
        self.trace_dir = trace_dir
        self.trace_tag = trace_tag
        
        self.collector = TraceCollector() if trace else None
        self.engine = Simulator(maxtime, debug=debug, collector=self.collector)
        self.graph = self._load_adjacency_matrix(self.filename)
        # Índice 0 reservado como None; nodos indexados desde 1
        self.table: list[Process | None] = [None] + [
            Process(row, self.engine, i)
            for i, row in enumerate(self.graph, start=1)
        ]

    def _load_adjacency_matrix(self, filename: str | Path) -> list[list[int]]:
        """Construye la topología G=(V,E) desde archivo."""
        return [
            [int(node) for node in line.split()]
            for line in Path(filename).read_text().splitlines()
            if line.strip()
        ]

    def set_model(self, model: Model, node_id: int) -> None:
        if process := self.table[node_id]:  # walrus operator: asigna y evalúa en una línea
            process.set_model(model)

    def init(self, event: Event) -> None:
        self.engine.insert_event(event)

    def _execute(self) -> None:
        """Bucle principal: extrae y enruta eventos hasta agotar la agenda."""
        from risansym.schemas import ReceiveEvent
        start_real_time = time.perf_counter()
        
        while self.engine.is_on:
            event = self.engine.pop_event()
            if process := self.table[event.target]:  # walrus operator
                process.set_time(event.time)
                process.receive(event)
                
                # Después de que el nodo procesó el evento, tomamos una "foto" (snapshot) de su estado interno
                state = process.model.get_state() if process.model else {}
                
                if self.collector:
                    self.collector.record(ReceiveEvent(
                        action="RECEIVE",
                        clock=event.time,
                        source=event.source,
                        target=event.target,
                        name=event.name,
                        payload=event.payload,
                        node_state=state
                    ))
                
        end_real_time = time.perf_counter()
        
        self.execution_metrics = {
            "simulated_time_elapsed": self.engine.clock,
            "total_messages": self.collector.get_event_count() if self.collector else 0,
            "execution_real_time_sec": round(end_real_time - start_real_time, 5)
        }
        
    def _save_trace(self) -> None:
        """Serializa y persiste la traza de eventos simulados con sus metadatos."""
        grafo_name = self.filename.stem
        tag = f"_{self.trace_tag}" if self.trace_tag else ""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if isinstance(self.trace, (str, Path)) and not isinstance(self.trace, bool):
            trace_path = Path(self.trace)
        else:
            file_name = f"{self.algo_name}_{grafo_name}{tag}_{timestamp}.json"
            trace_path = Path(self.trace_dir) / self.algo_name / file_name
            
        total_edges = sum(len(neighbors) for neighbors in self.graph)
        total_nodes = len(self.table) - 1
        
        metadata = TraceMetadata(
            schema_version="1.0",
            algorithm=self.algo_name,
            topology=grafo_name,
            tag=self.trace_tag,
            execution_date=timestamp,
            parameters={
                "max_time": self.engine.maxtime,
                "total_nodes": total_nodes,
                "total_edges": total_edges
            },
            metrics=self.execution_metrics
        )
        
        if self.collector:
            self.collector.dump(trace_path, metadata)

    def run(self) -> None:
        """Punto de entrada principal para ejecutar la simulación y guardar resultados."""
        self._execute()
        if self.trace:
            self._save_trace()
