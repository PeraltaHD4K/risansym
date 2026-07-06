# Writing Algorithms

In Risansym, distributed algorithms are defined by creating a class that inherits from `Model`. A model defines the behavior of a single node in your distributed network.

## The Model Class

Your custom algorithm must implement two core lifecycle methods:

1. `init(self)`: Called exactly once when the simulation starts. Use this to initialize state variables or send the first messages.
2. `receive(self, event: Event)`: Called every time the node receives a message from another node.

## Example: Ping-Pong Protocol

Let's build a simple algorithm where Node 1 sends a "PING" to Node 2, and Node 2 replies with a "PONG".

```python
import sys
import random
from risansym import Model, Event, Simulation

class AlgorithmPingPong(Model):
    
    def init(self) -> None:
        # We assume the first neighbor in the list is our successor
        self.sucesor = self.neighbors[0]
        self.contador = 0
        self.log(f"Inicializado. Mi vecino es el Nodo {self.sucesor}")

    def receive(self, event: Event) -> None:
        retraso = float(random.randint(1, 3))
        
        match event.name:
            case "INICIA":
                self.log("Recibe INICIA. ¡Saque inicial!")
                self.transmit(Event(time=self.clock + retraso, name="PING", target=self.sucesor, source=self.id))
                
            case "PING":
                self.contador += 1
                self.log(f"Recibe PING #{self.contador}. Devolviendo PONG...")
                self.transmit(Event(time=self.clock + retraso, name="PONG", target=self.sucesor, source=self.id))
                
            case "PONG":
                self.contador += 1
                self.log(f"Recibe PONG #{self.contador}. Devolviendo PING...")
                self.transmit(Event(time=self.clock + retraso, name="PING", target=self.sucesor, source=self.id))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Error: Proporcione el archivo de red (ej. g0.txt)")

    # Simulación acotada a 15.0 unidades de tiempo para que no sea infinita
    experiment = Simulation.from_file(
        filename=sys.argv[1], 
        maxtime=15.0, 
        algo_name="AlgorithmPingPong", 
        debug=True, 
        trace=True
    )  

    # Cargar los modelos en los procesos
    for i in range(1, len(experiment.graph) + 1):
        experiment.set_model(AlgorithmPingPong(), i)

    # Iniciar explícitamente los modelos (Requerido en >=v0.4.0)
    experiment.initialize_all()

    # Inyectar el evento semilla en el Nodo 1
    experiment.init(Event(time=0.0, name="INICIA", target=1, source=1))

    print("=== Iniciando Prueba Ping Pong ===")
    experiment.run()
    print("=== Fin de la Simulación ===")
```

## State Snapshots

For advanced use cases (and better visualizer data), you can implement `get_state()` in your model. This method takes a snapshot of your node's internal state after processing every event.

```python
class AdvancedModel(Model):
    def __init__(self):
        self.messages_processed = 0

    def receive(self, event: Event):
        self.messages_processed += 1

    def get_state(self) -> dict:
        return {
            "processed": self.messages_processed
        }
```
This state will be stored inside the generated trace file and displayed in the Web Visualizer when clicking on events.
