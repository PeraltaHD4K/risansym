# Welcome to Risansym

**Risansym** is a typed Python discrete-event simulation library for designing,
executing, and analyzing distributed algorithms.

The Python engine is the primary product. An optional React/Next.js application
can visualize versioned JSON traces produced by an attached tracer plugin.

---

## Why Risansym?

- **Explicit contracts:** Typed events, validated topologies, structured results,
  and domain exceptions.
- **Reproducible topologies:** Deterministic generators accept a seed or an
  explicit random-number generator.
- **Composable observability:** Console logging and JSON tracing are plugins,
  not engine configuration.
- **Decoupled visualization:** Trace consumers do not need access to the
  simulation process.
- **Incremental execution:** Step, stop, resume, or run to a simulated-time
  boundary.

## Next Steps

- Jump into the **[Getting Started](tutorial/getting_started.md)** guide to install the library.
- Create or load a graph with **[Creating Topologies](tutorial/topologies.md)**.
- Learn how to build your first protocol in the **[Writing Algorithms](tutorial/writing_algorithms.md)** tutorial.
- Add tracing or custom integrations with **[Plugins](tutorial/plugins.md)**.
- Explore the **[API Reference](api/simulation.md)** for detailed documentation on the framework's classes.
