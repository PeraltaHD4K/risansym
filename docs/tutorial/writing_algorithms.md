# Writing Algorithms

In Risansym, distributed algorithms are defined by creating a class that inherits from `Model`. A model defines the behavior of a single node in your distributed network.

## The Model Class

Your custom algorithm must implement two core lifecycle methods:

1. `init(self)`: Called exactly once when the simulation starts. Use this to initialize state variables or send the first messages.
2. `receive(self, event: Event)`: Called every time the node receives a message from another node.

## Example: Ping-Pong Protocol

Let's build a simple algorithm where Node 1 sends a "PING" to Node 2, and Node 2 replies with a "PONG".

```python
import random
from risansym import Model, Event, Simulation

class AlgorithmPingPong(Model):
    
    def init(self) -> None:
        # We assume the first neighbor in the list is our successor
        self.successor = self.neighbors[0]
        self.counter = 0
        self.log(f"Initialized. My neighbor is Node {self.successor}")

    def receive(self, event: Event) -> None:
        delay = float(random.randint(1, 3))
        
        match event.name:
            case "START":
                self.log("Received START. Initiating sequence!")
                self.transmit(Event(time=self.clock + delay, name="PING", target=self.successor, source=self.node_id))
                
            case "PING":
                self.counter += 1
                self.log(f"Received PING #{self.counter}. Returning PONG...")
                self.transmit(Event(time=self.clock + delay, name="PONG", target=self.successor, source=self.node_id))
                
            case "PONG":
                self.counter += 1
                self.log(f"Received PONG #{self.counter}. Returning PING...")
                self.transmit(Event(time=self.clock + delay, name="PING", target=self.successor, source=self.node_id))
```

## Attaching the Algorithm

Once you define your class, you bind instances of it to the simulation nodes:

```python
# Create the simulation engine reading from our topology file
experiment = Simulation.from_file(
    filename="graph.txt", 
    maxtime=15.0, 
    algo_name="AlgorithmPingPong", 
    debug=True, 
    trace=True
)  

# Bind a fresh instance of the model to every node in the graph
for i in range(1, len(experiment.graph) + 1):
    experiment.set_model(AlgorithmPingPong(), i)

# Explicitly initialize all models (Required in >=v0.4.0)
experiment.initialize_all()

# Inject the seed event into Node 1
experiment.init(Event(time=0.0, name="START", target=1, source=1))

print("=== Starting Ping Pong Simulation ===")
experiment.run()
print("=== End of Simulation ===")
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
