# System Architecture

Risansym operates as two completely decoupled systems: a **Python Engine** and a **Web Visualizer**. They communicate strictly through serialized JSON trace files.

## The Python Engine (Core)

The core is a classic **Discrete Event Simulator (DES)** built entirely in Python.

### Simulation Loop
At the heart of the engine is an internal agenda. It maintains a global clock and a Priority Queue (Min-Heap).
When an `Event` is transmitted, it is pushed into the priority queue, sorted primarily by its `time` attribute.
The main loop pops the event with the lowest timestamp, advances the global clock to that time, and invokes the `receive` callback on the target `Process`.

### Processes and Models
An internal process wrapper represents each topology node. A `Model` is the
user-defined algorithm behavior and is bound to a node through
`Simulation.set_model()`.

`Simulation`, `Model`, `Event`, lifecycle results, plugin contracts, topology
helpers, and domain exceptions form the stable 1.0 API. Agenda, process,
builder, exporter, plugin-manager, and collector implementations are internal
and may evolve without compatibility guarantees.

## The Web Visualizer (React)

The visualizer is built using React and Next.js. It loads the JSON trace file into a statically typed format using `Zod`.

The Pydantic `TraceOutput` model is the source of truth. Its generated JSON
Schema is checked into `shared/schema/trace.schema.json`; shared valid and
invalid fixtures prevent the Python and TypeScript validators from drifting.

### Rendering
The timeline is drawn using SVG elements. 
The visualizer maps time to the X-axis and nodes to the Y-axis (lifelines).

### Animation
The playback engine uses `requestAnimationFrame` to compute a smooth delta-time interpolation. 
Pending messages are rendered dynamically. Since network transmission occurs over a period of time, the message is drawn as a smooth Bézier curve using the De Casteljau algorithm between the source and target coordinates.
