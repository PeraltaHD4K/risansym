# Graph Report - .  (2026-07-24)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 522 nodes · 1016 edges · 33 communities (25 shown, 8 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 101 edges (avg confidence: 0.5)
- Token cost: 1,452 input · 351 output

## Graph Freshness
- Built from commit: `19a0e722`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Web UI Components
- Simulation Engine Core
- Trace Export Logic
- Simulation Plugin System
- Project Dependencies
- Base Model Interface
- TypeScript Configuration
- Topology Loading Tests
- Topology Generation Utilities
- Event Management System
- Public API Tests
- Model Behavior Tests
- React Error Boundary
- Project Documentation
- Simulation Integration Tests
- Event Validation Tests
- Event Payload Tests
- Message Sink Protocol
- Event Ordering Tests
- Echo Model Implementation
- Event Delegation Logic
- Event Heap Management
- Test Fixtures
- ESLint Configuration
- Next.js Configuration
- Project Identity

## God Nodes (most connected - your core abstractions)
1. `Event` - 75 edges
2. `Simulator` - 50 edges
3. `Simulation` - 47 edges
4. `Model` - 30 edges
5. `Process` - 30 edges
6. `TraceCollector` - 23 edges
7. `JSONTracerPlugin` - 19 edges
8. `AppLogEvent` - 17 edges
9. `SimulationPlugin` - 16 edges
10. `TransmitEvent` - 16 edges

## Surprising Connections (you probably didn't know these)
- `Simulation` --uses--> `SimulationBuilder`  [INFERRED]
  core/src/risansym/simulation.py → core/src/risansym/engine/builder.py
- `TraceExporter` --uses--> `Process`  [INFERRED]
  core/src/risansym/engine/exporter.py → core/src/risansym/process.py
- `JSONTracerPlugin` --uses--> `TraceExporter`  [INFERRED]
  core/src/risansym/plugins/tracer.py → core/src/risansym/engine/exporter.py
- `Simulation` --uses--> `EventLoop`  [INFERRED]
  core/src/risansym/simulation.py → core/src/risansym/engine/loop.py
- `MessageSink` --uses--> `Event`  [INFERRED]
  core/src/risansym/model.py → core/src/risansym/event.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Risansym System Flow** — python_engine, trace_files, web_visualizer [EXTRACTED 1.00]

## Communities (33 total, 8 thin omitted)

### Community 0 - "Web UI Components"
Cohesion: 0.06
Nodes (54): inter, metadata, outfit, Home(), PlaybackControls(), MockFileReader, Uploader(), MESSAGE_COLORS (+46 more)

### Community 1 - "Simulation Engine Core"
Cohesion: 0.06
Nodes (40): Path, Handles the construction of the simulation graph and components., Load or pass through the topology graph and determine its name., Construct the process table based on the topology graph., SimulationBuilder, EventLoop, Any, Executes the simulation event loop and routes messages. (+32 more)

### Community 2 - "Trace Export Logic"
Cohesion: 0.07
Nodes (30): BaseModel, Any, Path, Handles serialization and persistence of the simulation trace., Serialize and persist the trace with metadata., TraceExporter, AppLogEvent, Recorded when a node processes an incoming message. (+22 more)

### Community 3 - "Simulation Plugin System"
Cohesion: 0.05
Nodes (29): BaseException, Called just before the simulation event loop begins., Called when the simulation loop has finished., ConsoleLoggerPlugin, Logs simulation events to the standard output., JSONTracerPlugin, Path, Records simulation events and exports them to a JSON trace file. (+21 more)

### Community 4 - "Project Dependencies"
Cohesion: 0.05
Nodes (42): eslint, eslint-config-next, jsdom, lucide-react, next, react, react-dom, @testing-library/dom (+34 more)

### Community 5 - "Base Model Interface"
Cohesion: 0.07
Nodes (16): ABC, Model, Any, Return a snapshot of the node's internal state.          Override in subclasses, Initialize local state (implemented by the subclass)., State-machine transition logic (implemented by the subclass)., Abstract interface (contract) for distributed algorithms.      Subclasses must i, Advance the node's local clock (called by the framework). (+8 more)

### Community 6 - "TypeScript Configuration"
Cohesion: 0.07
Nodes (28): dom, dom.iterable, esnext, **/*.mts, .next/dev/types/**/*.ts, next-env.d.ts, .next/types/**/*.ts, node_modules (+20 more)

### Community 7 - "Topology Loading Tests"
Cohesion: 0.20
Nodes (8): Path, Factory method to instantiate a Simulation from a topology file., make_topo(), Tests for topology loading and validation in Simulation., Factory fixture that writes a topology file and returns its path., TestTopologyValidation, Create a 2-node simulation with trace enabled., two_node_sim()

### Community 8 - "Topology Generation Utilities"
Cohesion: 0.13
Nodes (10): Path, Exports the adjacency matrix to a text file format readable by Simulation.from_f, test_export_to_file(), test_line_topology(), test_line_unidirectional(), test_mesh_topology(), test_random_topology(), test_ring_topology() (+2 more)

### Community 9 - "Event Management System"
Cohesion: 0.16
Nodes (6): Event, Encapsulates the information exchanged between active processes in the simulatio, Any, Any, Deliver an incoming event to the bound model for processing., Pop the nearest event and advance the global clock.          Raises:

### Community 10 - "Public API Tests"
Cohesion: 0.15
Nodes (3): Tests for the public API exposed via __init__.py., Verify that all symbols are importable from the top-level package., TestPublicAPI

### Community 11 - "Model Behavior Tests"
Cohesion: 0.31
Nodes (7): DummyModel, __repr__ should show updated node_id when bound., test_model_id_deprecation(), test_model_repr(), test_model_repr_bound(), test_model_unbound_log(), test_model_unbound_transmit()

### Community 12 - "React Error Boundary"
Cohesion: 0.25
Nodes (3): ErrorBoundary, Props, State

### Community 13 - "Project Documentation"
Cohesion: 0.29
Nodes (3): Python Engine (Core), JSON Trace Files, Web Visualizer (React)

### Community 14 - "Simulation Integration Tests"
Cohesion: 0.33
Nodes (4): DummyModel, test_basic_simulation(), test_simulation_deprecated_path_warning(), test_simulation_trace_warning()

### Community 15 - "Event Validation Tests"
Cohesion: 0.33
Nodes (3): Tests for the Event dataclass., Verify Event construction validation and argument order., TestEventValidation

### Community 16 - "Event Payload Tests"
Cohesion: 0.33
Nodes (3): Verify payload typing and defaults., Ensure default_factory creates separate dicts per instance., TestEventPayload

### Community 17 - "Message Sink Protocol"
Cohesion: 0.40
Nodes (3): MessageSink, Protocol, Protocol defining what a Model needs from its host environment.

## Knowledge Gaps
- **73 isolated node(s):** `risansym`, `eslintConfig`, `nextConfig`, `name`, `version` (+68 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Event` connect `Event Management System` to `Simulation Engine Core`, `Trace Export Logic`, `Simulation Plugin System`, `Base Model Interface`, `Model Behavior Tests`, `Simulation Integration Tests`, `Event Validation Tests`, `Event Payload Tests`, `Message Sink Protocol`, `Event Ordering Tests`, `Echo Model Implementation`, `Event Delegation Logic`, `Event Heap Management`?**
  _High betweenness centrality (0.126) - this node is a cross-community bridge._
- **Why does `Simulation` connect `Simulation Plugin System` to `Simulation Engine Core`, `Trace Export Logic`, `Base Model Interface`, `Topology Loading Tests`, `Event Management System`, `Simulation Integration Tests`, `Echo Model Implementation`?**
  _High betweenness centrality (0.085) - this node is a cross-community bridge._
- **Why does `Simulator` connect `Simulation Engine Core` to `Event Management System`, `Trace Export Logic`, `Simulation Plugin System`, `Event Heap Management`?**
  _High betweenness centrality (0.056) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Event` (e.g. with `MessageSink` and `Model`) actually correct?**
  _`Event` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `Simulator` (e.g. with `SimulationBuilder` and `EventLoop`) actually correct?**
  _`Simulator` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `Simulation` (e.g. with `SimulationPlugin` and `ConsoleLoggerPlugin`) actually correct?**
  _`Simulation` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `Model` (e.g. with `Event` and `EngineProtocol`) actually correct?**
  _`Model` has 13 INFERRED edges - model-reasoned connections that need verification._