# Writing Algorithms

In Risansym, distributed algorithms are defined by creating a class that inherits from `Model`. A model defines the behavior of a single node in your distributed network.

## The Model Class

Your custom algorithm must implement two core lifecycle methods:

1. `init(self)`: Called exactly once when the simulation starts. Use this to initialize state variables or send the first messages.
2. `receive(self, event: Event)`: Called every time the node receives a message from another node.

## Example: Ping-Pong Protocol

Let's build a simple algorithm where Node 1 sends a "PING" to Node 2, and Node 2 replies with a "PONG".

```python
from risansym import Model, Event, Simulation

class PingPong(Model):
    def init(self):
        # We start the protocol if we are node 1
        if self.id == 1:
            # We assume node 2 is our neighbor
            target = self.neighbors[0]
            # Send the PING event to arrive at time = clock + 1.0
            self.transmit(Event(
                time=self.clock + 1.0, 
                name="PING", 
                target=target, 
                source=self.id
            ))
            self.log(f"Started ping to node {target}")

    def receive(self, event: Event):
        self.log(f"Received {event.name} from node {event.source}")
        
        # If we receive PING, reply with PONG
        if event.name == "PING":
            self.transmit(Event(
                time=self.clock + 1.0,
                name="PONG",
                target=event.source,
                source=self.id
            ))
```

## Attaching the Algorithm

Once you define your class, you bind instances of it to the simulation nodes:

```python
# Assuming graph.txt has at least 2 nodes
sim = Simulation.from_file("graph.txt", maxtime=10.0, debug=True)

# Bind a fresh instance of PingPong to every node in the graph
for i in range(1, len(sim.graph) + 1):
    sim.set_model(PingPong(), i)

sim.initialize_all()
sim.run()
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
