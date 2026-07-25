<div align="center">
  <img src="https://raw.githubusercontent.com/PeraltaHD4K/risansym/main/web/public/globe.svg" alt="Risansym logo" width="120" />
</div>

<h1 align="center">Risansym</h1>
<p align="center">
  <em>A typed discrete-event simulation library for distributed algorithms, with an optional web trace visualizer.</em>
</p>

<p align="center">
  <a href="https://github.com/PeraltaHD4K/risansym/actions/workflows/ci.yml"><img src="https://github.com/PeraltaHD4K/risansym/actions/workflows/ci.yml/badge.svg" alt="CI status"></a>
  <a href="https://pypi.org/project/risansym/"><img src="https://img.shields.io/pypi/v/risansym" alt="PyPI version"></a>
  <a href="https://pypi.org/project/risansym/"><img src="https://img.shields.io/pypi/pyversions/risansym" alt="Supported Python versions"></a>
  <a href="https://github.com/PeraltaHD4K/risansym/blob/main/LICENSE"><img src="https://img.shields.io/github/license/PeraltaHD4K/risansym" alt="MIT license"></a>
</p>

Risansym is a Python library for building reproducible discrete-event
simulations of distributed algorithms. The Python engine is the product's
primary component. The Next.js application in this repository is an optional
viewer for JSON traces produced by the engine.

## Installation

Risansym requires Python 3.10 or newer:

```bash
pip install risansym
```

## Quick start

```python
from risansym import Event, Model, Simulation, TopologyGenerator


class Receiver(Model):
    def init(self) -> None:
        pass

    def receive(self, event: Event) -> None:
        print(f"node {self.node_id} received {event.name} at t={self.clock}")


graph = TopologyGenerator.line(2)
simulation = Simulation(graph, maxtime=10.0)
simulation.set_model(Receiver(), 1)
simulation.set_model(Receiver(), 2)
simulation.initialize_all()
simulation.seed_event(Event(time=1.0, name="HELLO", source=1, target=2))

result = simulation.run()
assert result.complete
```

Observability is optional and composable:

```python
from risansym.plugins import ConsoleLoggerPlugin, JSONTracerPlugin

# Insert these lines after constructing the simulation and before initialize_all().
simulation.attach(ConsoleLoggerPlugin(trace_network=True, app_logs=True))
simulation.attach(JSONTracerPlugin("Receiver", trace_dir="traces"))
```

Plugins must be attached before `initialize_all()`.

## Topologies

Pass an adjacency list directly, generate a topology, or load one from an
adjacency list, edge list, or dense matrix:

```python
from risansym import Simulation, TopologyGenerator

graph = TopologyGenerator.random(100, probability=0.05, seed=42)
simulation = Simulation(graph, maxtime=1_000.0)
```

See the [topology guide](https://peraltahd4k.github.io/risansym/docs/tutorial/topologies/)
for generators, file formats, directed graphs, validation, and export.

## Documentation

- [Getting started](https://peraltahd4k.github.io/risansym/docs/tutorial/getting_started/)
- [Writing distributed algorithms](https://peraltahd4k.github.io/risansym/docs/tutorial/writing_algorithms/)
- [API reference](https://peraltahd4k.github.io/risansym/docs/api/simulation/)
- [Architecture](https://peraltahd4k.github.io/risansym/docs/architecture/)
- [Documentation map for coding agents](llms.txt)

## Repository layout

- `core/`: Python package, tests, benchmarks, and packaging configuration.
- `web/`: optional Next.js trace visualizer.
- `docs/`: user, API, architecture, and maintainer documentation.
- `shared/`: versioned JSON Schema and cross-language trace fixtures.

## Contributing and security

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. For
usage questions, see [SUPPORT.md](SUPPORT.md). Please report vulnerabilities
through the coordinated process in [SECURITY.md](SECURITY.md).

Risansym is distributed under the [MIT License](LICENSE).
