# Creating Topologies

Risansym represents a graph as an adjacency list. Node identifiers are
one-based: row zero describes node 1, row one describes node 2, and so on.

```python
# 1 -- 2 -- 3
graph = [[2], [1, 3], [2]]
```

`Simulation` validates and copies the graph. Empty rows represent isolated
nodes. Duplicate neighbors, references outside the graph, and self-loops are
rejected. Undirected graphs must contain both directions of every edge.

## Built-in generators

`TopologyGenerator` provides:

- `line(nodes)`
- `ring(nodes)`
- `star(nodes)`
- `mesh(nodes)`
- `tree(depth, branching_factor=2)`
- `random(nodes, probability=0.5)`

Use a generated graph directly:

```python
from risansym import Simulation, TopologyGenerator

graph = TopologyGenerator.ring(10)
simulation = Simulation(graph, maxtime=100.0)
```

Random topologies are weakly connected and reproducible when given a seed:

```python
graph = TopologyGenerator.random(
    100,
    probability=0.05,
    seed=42,
)
```

For experiment suites, an explicit `random.Random` instance lets the caller
control the random stream:

```python
import random

rng = random.Random(42)
first = TopologyGenerator.random(100, 0.05, rng=rng)
second = TopologyGenerator.random(100, 0.05, rng=rng)
```

Pass either `seed` or `rng`, never both.

## Directed graphs

Generators and loaders accept `directed=True`. A directed line contains edges
from each node to the next:

```python
graph = TopologyGenerator.line(4, directed=True)
simulation = Simulation(graph, maxtime=100.0, directed=True)
```

The same `directed` value must be used consistently when validating, exporting,
and constructing the simulation.

## Loading files

### Adjacency list

Each non-comment line represents one node. Blank data lines represent isolated
nodes:

```text
# node 1
2
# node 2
1 3
# node 3
2
```

```python
from risansym import load_adjacency_list

graph = load_adjacency_list("graph.txt")
```

### Edge list

Each data line contains a source and target:

```text
1 2
2 3
```

For undirected input, the loader creates the reverse adjacency. Use
`node_count` to preserve isolated nodes that do not appear in an edge:

```python
from risansym import load_edge_list

graph = load_edge_list("graph.edges", node_count=10)
```

### Dense matrix

Matrices must be square and contain only zeros and ones:

```text
0 1 0
1 0 1
0 1 0
```

```python
from risansym import load_dense_matrix

graph = load_dense_matrix("graph.matrix")
```

`Simulation.from_file()` provides the same loaders through the
`format="adjacency_list"`, `"edge_list"`, and `"dense_matrix"` values.

## Inspecting and exporting

```python
from risansym import describe_topology, export_adjacency_list, export_dot

print(describe_topology(graph))
export_adjacency_list(graph, "generated.txt")
export_dot(graph, "generated.dot")
```

DOT files can be rendered by Graphviz. Export validates the graph again but
does not mutate it.

## Routing implication

A topology is an execution contract, not only a visualization. A model may
transmit to itself or one of its direct neighbors. Messages to non-neighbors
must be forwarded by the distributed algorithm through intermediate nodes.
