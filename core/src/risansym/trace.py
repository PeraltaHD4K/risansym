import json
from pathlib import Path

class TraceCollector:
    """Responsable de acumular y persistir la traza de eventos simulados."""
    
    def __init__(self) -> None:
        self._trace: list[dict] = []

    def record(self, entry: dict) -> None:
        """Añade un evento estructurado a la traza en memoria."""
        self._trace.append(entry)
        
    def get_event_count(self) -> int:
        """Retorna el número de eventos registrados."""
        return len(self._trace)

    def dump(self, filepath: Path, metadata: dict) -> None:
        """Persiste la traza y metadatos en un archivo JSON."""
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with filepath.open('w', encoding='utf-8') as f:
            output = {
                "metadata": metadata,
                "trace": self._trace
            }
            json.dump(output, f, indent=2, ensure_ascii=False)
