import json
from pathlib import Path
from risansym.schemas import TraceEvent, TraceMetadata, TraceOutput

class TraceCollector:
    """Responsable de acumular y persistir la traza de eventos simulados usando Pydantic."""
    
    def __init__(self) -> None:
        self._trace: list[TraceEvent] = []

    def record(self, entry: TraceEvent) -> None:
        """Añade un evento estructurado a la traza en memoria."""
        self._trace.append(entry)
        
    def get_event_count(self) -> int:
        """Retorna el número de eventos registrados."""
        return len(self._trace)

    def dump(self, filepath: Path, metadata: TraceMetadata) -> None:
        """Persiste la traza validada matemáticamente en un archivo JSON."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Validar y armar el objeto final
        output = TraceOutput(metadata=metadata, trace=self._trace)
        
        # Guardar en disco
        with filepath.open('w', encoding='utf-8') as f:
            f.write(output.model_dump_json(indent=2))
