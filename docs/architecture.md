# System Architecture

Risansym operates as two completely decoupled systems: a **Python Engine** and a **Web Visualizer**. They communicate strictly through serialized JSON trace files.

## The Python Engine (Core)

The core is a classic **Discrete Event Simulator (DES)** built entirely in Python.

### Simulation Loop
At the heart of the engine is the `Simulator` (or Agenda). It maintains a global clock and a Priority Queue (Min-Heap).
When an `Event` is transmitted, it is pushed into the priority queue, sorted primarily by its `time` attribute.
The main loop pops the event with the lowest timestamp, advances the global clock to that time, and invokes the `receive` callback on the target `Process`.

### Processes and Models
A `Process` represents a physical node wrapper in the topology graph. It holds metadata (like its `id` and `neighbors`).
A `Model` is the user-defined algorithm behavior. When a user creates a simulation, they map instances of their `Model` to `Process` nodes.

## The Web Visualizer (React)

The visualizer is built using React and Next.js. It loads the JSON trace file into a statically typed format using `Zod`.

### Rendering
The timeline is drawn using SVG elements. 
The visualizer maps time to the X-axis and nodes to the Y-axis (lifelines).

### Animation
The playback engine uses `requestAnimationFrame` to compute a smooth delta-time interpolation. 
Pending messages are rendered dynamically. Since network transmission occurs over a period of time, the message is drawn as a smooth Bézier curve using the De Casteljau algorithm between the source and target coordinates.
