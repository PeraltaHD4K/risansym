"""Topology loading, validation, generation, and export."""

from __future__ import annotations

import random
from collections.abc import Sequence
from pathlib import Path

from risansym.exceptions import ConfigurationError, TopologyError

AdjacencyList = list[list[int]]


def normalize_topology(
    graph: Sequence[Sequence[int]],
    *,
    directed: bool,
    allow_self_loops: bool = False,
) -> AdjacencyList:
    """Validate and copy an adjacency-list topology.

    Node identifiers are one-based. Empty rows represent isolated nodes.
    Duplicate neighbors are rejected rather than silently discarded.
    """
    if isinstance(graph, (str, bytes)) or not isinstance(graph, Sequence):
        raise TopologyError("Topology must be a sequence of neighbor sequences.")
    if not isinstance(directed, bool):
        raise ConfigurationError("directed must be a boolean.")
    if not graph:
        raise TopologyError("A topology must contain at least one node.")

    normalized: AdjacencyList = []
    node_count = len(graph)

    for node_id, row in enumerate(graph, start=1):
        if isinstance(row, (str, bytes)) or not isinstance(row, Sequence):
            raise TopologyError(f"Neighbors for node {node_id} must be a sequence.")

        neighbors: list[int] = []
        seen: set[int] = set()
        for neighbor in row:
            if not isinstance(neighbor, int) or isinstance(neighbor, bool):
                raise TopologyError(f"Node {node_id} has non-integer neighbor {neighbor!r}.")
            if neighbor < 1 or neighbor > node_count:
                raise TopologyError(
                    f"Node {node_id} references node {neighbor}, outside the valid "
                    f"range 1-{node_count}."
                )
            if neighbor == node_id and not allow_self_loops:
                raise TopologyError(f"Node {node_id} contains a self-loop, which is not allowed.")
            if neighbor in seen:
                raise TopologyError(f"Node {node_id} contains duplicate neighbor {neighbor}.")
            seen.add(neighbor)
            neighbors.append(neighbor)

        normalized.append(neighbors)

    if not directed:
        neighbor_sets = [set(row) for row in normalized]
        for node_id, neighbors in enumerate(normalized, start=1):
            for neighbor in neighbors:
                if node_id not in neighbor_sets[neighbor - 1]:
                    raise TopologyError(
                        f"Undirected topology is asymmetric: node {node_id} references "
                        f"node {neighbor}, but the reverse edge is missing."
                    )

    return normalized


def _require_file(filename: str | Path) -> Path:
    path = Path(filename)
    if not path.exists():
        raise FileNotFoundError(f"Topology file '{path}' does not exist.")
    if not path.is_file():
        raise IsADirectoryError(f"Topology path '{path}' is not a regular file.")
    return path


def load_adjacency_list(
    filename: str | Path,
    *,
    directed: bool = False,
) -> AdjacencyList:
    """Load a topology whose data rows list each node's neighbors.

    Blank data rows represent isolated nodes. Lines beginning with ``#`` are
    comments and do not represent nodes.
    """
    path = _require_file(filename)
    graph: AdjacencyList = []

    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        stripped = raw_line.strip()
        if stripped.startswith("#"):
            continue
        if not stripped:
            graph.append([])
            continue
        try:
            graph.append([int(token) for token in stripped.split()])
        except ValueError as error:
            raise TopologyError(
                f"Invalid adjacency list '{path}' at line {line_number}: "
                "neighbors must be integers."
            ) from error

    return normalize_topology(graph, directed=directed)


def load_edge_list(
    filename: str | Path,
    *,
    directed: bool = False,
    node_count: int | None = None,
) -> AdjacencyList:
    """Load a topology containing one ``source target`` edge per data row.

    For undirected topologies, each input pair denotes one undirected edge and
    the reverse adjacency is generated automatically. ``node_count`` can be
    supplied to preserve isolated nodes that do not occur in any edge.
    """
    path = _require_file(filename)
    if node_count is not None:
        if not isinstance(node_count, int) or isinstance(node_count, bool) or node_count < 1:
            raise ConfigurationError("node_count must be a positive integer.")

    edges: list[tuple[int, int]] = []
    maximum_node = 0

    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split()
        if len(parts) != 2:
            raise TopologyError(
                f"Invalid edge list '{path}' at line {line_number}: expected exactly two integers."
            )
        try:
            source, target = (int(part) for part in parts)
        except ValueError as error:
            raise TopologyError(
                f"Invalid edge list '{path}' at line {line_number}: "
                "edge endpoints must be integers."
            ) from error
        if source < 1 or target < 1:
            raise TopologyError(
                f"Invalid edge list '{path}' at line {line_number}: "
                "node identifiers must be positive."
            )
        maximum_node = max(maximum_node, source, target)
        edges.append((source, target))

    total_nodes = node_count if node_count is not None else maximum_node
    if total_nodes < maximum_node:
        raise TopologyError(
            f"node_count={total_nodes} is smaller than referenced node {maximum_node}."
        )
    if total_nodes == 0:
        raise TopologyError("An edge list without edges requires a positive node_count.")

    graph: AdjacencyList = [[] for _ in range(total_nodes)]
    for source, target in edges:
        graph[source - 1].append(target)
        if not directed and source != target:
            graph[target - 1].append(source)

    return normalize_topology(graph, directed=directed)


def load_dense_matrix(
    filename: str | Path,
    *,
    directed: bool = False,
) -> AdjacencyList:
    """Load a strict square adjacency matrix containing only zeros and ones."""
    path = _require_file(filename)
    matrix: list[list[int]] = []

    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            row = [int(token) for token in stripped.split()]
        except ValueError as error:
            raise TopologyError(
                f"Invalid dense matrix '{path}' at line {line_number}: "
                "matrix cells must be integers."
            ) from error
        if any(value not in (0, 1) for value in row):
            raise TopologyError(
                f"Invalid dense matrix '{path}' at line {line_number}: matrix cells must be 0 or 1."
            )
        matrix.append(row)

    size = len(matrix)
    if size == 0:
        raise TopologyError("A dense matrix must contain at least one row.")
    for row_number, row in enumerate(matrix, start=1):
        if len(row) != size:
            raise TopologyError(
                f"Dense matrix must be square: row {row_number} has {len(row)} "
                f"columns, expected {size}."
            )

    graph: AdjacencyList = [
        [target for target, connected in enumerate(row, start=1) if connected == 1]
        for row in matrix
    ]
    return normalize_topology(graph, directed=directed)


class TopologyGenerator:
    """Generate validated topologies in adjacency-list format."""

    @staticmethod
    def line(nodes: int, *, directed: bool = False) -> AdjacencyList:
        graph = _empty_graph(nodes)
        for source in range(nodes - 1):
            graph[source].append(source + 2)
            if not directed:
                graph[source + 1].append(source + 1)
        return normalize_topology(graph, directed=directed)

    @staticmethod
    def ring(nodes: int, *, directed: bool = False) -> AdjacencyList:
        graph = TopologyGenerator.line(nodes, directed=directed)
        if nodes > 2:
            graph[-1].append(1)
            if not directed:
                graph[0].append(nodes)
        graph = [sorted(neighbors) for neighbors in graph]
        return normalize_topology(graph, directed=directed)

    @staticmethod
    def star(nodes: int, *, directed: bool = False) -> AdjacencyList:
        graph = _empty_graph(nodes)
        for target in range(2, nodes + 1):
            graph[0].append(target)
            if not directed:
                graph[target - 1].append(1)
        return normalize_topology(graph, directed=directed)

    @staticmethod
    def mesh(nodes: int, *, directed: bool = False) -> AdjacencyList:
        graph = _empty_graph(nodes)
        for source in range(1, nodes + 1):
            graph[source - 1] = [target for target in range(1, nodes + 1) if target != source]
        return normalize_topology(graph, directed=directed)

    @staticmethod
    def tree(
        depth: int,
        branching_factor: int = 2,
        *,
        directed: bool = False,
    ) -> AdjacencyList:
        if not isinstance(depth, int) or isinstance(depth, bool) or depth < 0:
            raise ConfigurationError("depth must be a non-negative integer.")
        if (
            not isinstance(branching_factor, int)
            or isinstance(branching_factor, bool)
            or branching_factor < 1
        ):
            raise ConfigurationError("branching_factor must be a positive integer.")

        nodes = sum(branching_factor**level for level in range(depth + 1))
        graph = _empty_graph(nodes)
        for parent in range(nodes):
            for child_offset in range(1, branching_factor + 1):
                child = parent * branching_factor + child_offset
                if child >= nodes:
                    break
                graph[parent].append(child + 1)
                if not directed:
                    graph[child].append(parent + 1)
        return normalize_topology(graph, directed=directed)

    @staticmethod
    def random(
        nodes: int,
        probability: float = 0.5,
        *,
        directed: bool = False,
        seed: int | None = None,
        rng: random.Random | None = None,
    ) -> AdjacencyList:
        """Generate a reproducible weakly connected random topology."""
        graph = _empty_graph(nodes)
        if not isinstance(probability, (int, float)) or isinstance(probability, bool):
            raise ConfigurationError("probability must be a number.")
        if not 0.0 <= probability <= 1.0:
            raise ConfigurationError("probability must be between 0.0 and 1.0.")
        if seed is not None and rng is not None:
            raise ConfigurationError("Pass either seed or rng, not both.")
        generator = rng if rng is not None else random.Random(seed)
        if not isinstance(generator, random.Random):
            raise ConfigurationError("rng must be an instance of random.Random.")

        graph_sets: list[set[int]] = [set() for _ in range(nodes)]
        unvisited = list(range(1, nodes))
        generator.shuffle(unvisited)
        visited = [0]
        for node in unvisited:
            parent = generator.choice(visited)
            graph_sets[parent].add(node + 1)
            if not directed:
                graph_sets[node].add(parent + 1)
            visited.append(node)

        if directed:
            for source in range(nodes):
                for target in range(nodes):
                    if source == target or target + 1 in graph_sets[source]:
                        continue
                    if generator.random() < probability:
                        graph_sets[source].add(target + 1)
        else:
            for source in range(nodes):
                for target in range(source + 1, nodes):
                    if target + 1 in graph_sets[source]:
                        continue
                    if generator.random() < probability:
                        graph_sets[source].add(target + 1)
                        graph_sets[target].add(source + 1)

        graph = [sorted(neighbors) for neighbors in graph_sets]
        return normalize_topology(graph, directed=directed)

    @staticmethod
    def show(graph: Sequence[Sequence[int]]) -> None:
        """Print a compact human-readable connectivity map."""
        nodes = len(graph)
        edges = sum(len(neighbors) for neighbors in graph)
        print(f"Topology Info: {nodes} nodes, {edges} directed edges")
        print("Connectivity Map:")
        limit = min(nodes, 5 if nodes > 15 else nodes)
        if nodes > 15:
            print(" (Graph too large to display entirely, showing first 5 nodes)")
        for index in range(limit):
            print(f"Node {index + 1} -> {list(graph[index])}")
        if nodes > 15:
            print(" ...")

    @staticmethod
    def export_adjacency_list(
        graph: Sequence[Sequence[int]],
        filename: str | Path,
        *,
        directed: bool = False,
    ) -> None:
        """Validate and export a topology in adjacency-list format."""
        normalized = normalize_topology(graph, directed=directed)
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as file:
            for neighbors in normalized:
                file.write(" ".join(str(neighbor) for neighbor in neighbors) + "\n")

    @staticmethod
    def export_dot(
        graph: Sequence[Sequence[int]],
        filename: str | Path,
        *,
        directed: bool = False,
    ) -> None:
        """Validate and export a topology in Graphviz DOT format."""
        normalized = normalize_topology(graph, directed=directed)
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        graph_type = "digraph" if directed else "graph"
        connector = "->" if directed else "--"
        seen_edges: set[tuple[int, int]] = set()

        with path.open("w", encoding="utf-8") as file:
            file.write(f"{graph_type} G {{\n")
            file.write("  node [shape=circle];\n")
            for source, neighbors in enumerate(normalized, start=1):
                if not neighbors:
                    file.write(f"  {source};\n")
                for target in neighbors:
                    edge = (
                        (source, target) if directed else (min(source, target), max(source, target))
                    )
                    if edge in seen_edges:
                        continue
                    seen_edges.add(edge)
                    file.write(f"  {source} {connector} {target};\n")
            file.write("}\n")


def _empty_graph(nodes: int) -> AdjacencyList:
    if not isinstance(nodes, int) or isinstance(nodes, bool) or nodes < 1:
        raise ConfigurationError("nodes must be a positive integer.")
    return [[] for _ in range(nodes)]
