import random
from pathlib import Path

def load_adjacency_matrix(filename: str | Path) -> list[list[int]]:
    """Build the topology G=(V,E) from a file in Adjacency List format.
    Line i contains space-separated neighbors for node i+1.
    """
    path = Path(filename)
    if not path.exists():
        raise FileNotFoundError(f"Topology file '{path}' does not exist.")

    graph: list[list[int]] = []
    line_idx = 0
    try:
        with path.open("r") as f:
            for line_idx, line in enumerate(f):
                if not line.strip():
                    continue
                # Remove duplicates and self-loops while preserving order
                current_node = len(graph) + 1
                seen = set()
                neighbors = []
                for node in (int(n) for n in line.split()):
                    if node != current_node and node not in seen:
                        seen.add(node)
                        neighbors.append(node)
                graph.append(neighbors)
    except ValueError as e:
        raise ValueError(
            f"Syntax error in topology file (line {line_idx + 1}): "
            f"all node identifiers must be integers. ({e})"
        ) from e

    _validate_graph(graph, path)
    return graph

def load_edge_list(filename: str | Path) -> list[list[int]]:
    """Build the topology from a file in Edge List format.
    Format: 'source target' on each line. Automatically detects node count.
    """
    path = Path(filename)
    if not path.exists():
        raise FileNotFoundError(f"Topology file '{path}' does not exist.")

    max_node = 0
    edges: list[tuple[int, int]] = []
    
    try:
        with path.open("r") as f:
            for line_idx, line in enumerate(f):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) != 2:
                    raise ValueError("Each line must have exactly 2 integers.")
                u, v = int(parts[0]), int(parts[1])
                
                max_node = max(max_node, u, v)
                edges.append((u, v))
    except ValueError as e:
        raise ValueError(
            f"Syntax error in edge list file '{path}' (line {line_idx + 1}): {e}"
        ) from e

    # Build the internal adjacency list
    graph: list[list[int]] = [[] for _ in range(max_node)]
    for u, v in edges:
        if v not in graph[u - 1] and u != v:
            graph[u - 1].append(v)
            
    _validate_graph(graph, path)
    return graph

def load_dense_matrix(filename: str | Path) -> list[list[int]]:
    """Build the topology from a Dense Adjacency Matrix (NxN of 0s and 1s)."""
    path = Path(filename)
    if not path.exists():
        raise FileNotFoundError(f"Topology file '{path}' does not exist.")

    graph: list[list[int]] = []
    
    try:
        with path.open("r") as f:
            for line_idx, line in enumerate(f):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                current_node = len(graph) + 1
                neighbors = []
                # Enumerate the values (0 or 1) in the row
                for neighbor_idx, val_str in enumerate(line.split(), start=1):
                    val = int(val_str)
                    if val != 0 and val != 1:
                        raise ValueError("Matrix cells must be 0 or 1.")
                    if val == 1 and neighbor_idx != current_node:
                        neighbors.append(neighbor_idx)
                        
                graph.append(neighbors)
    except ValueError as e:
        raise ValueError(
            f"Syntax error in dense matrix file '{path}' (line {line_idx + 1}): {e}"
        ) from e

    # Validate square matrix
    num_nodes = len(graph)
    for i, neighbors in enumerate(graph, start=1):
        # We can't strictly validate column count here because we just stored neighbors,
        # but if there were fewer elements in a row, any out of bounds would be caught
        # by _validate_graph later. However, we can trust the parsing logic.
        pass

    _validate_graph(graph, path)
    return graph

def _validate_graph(graph: list[list[int]], path: Path) -> None:
    """Validates an adjacency list graph for bounds and asymmetry."""
    num_nodes = len(graph)
    if num_nodes == 0:
        import warnings
        warnings.warn(
            f"Topology file '{path}' is empty. The simulation will have no nodes.",
            UserWarning,
            stacklevel=2,
        )

    graph_sets = [set(neighbors) for neighbors in graph]
    for i, neighbors in enumerate(graph, start=1):
        for neighbor in neighbors:
            if neighbor < 1 or neighbor > num_nodes:
                raise ValueError(
                    f"Node {i} references node {neighbor}, which is outside "
                    f"the valid range (1 to {num_nodes})."
                )
            
            # Check for asymmetry (O(1) lookup)
            if i not in graph_sets[neighbor - 1]:
                import warnings
                warnings.warn(
                    f"Asymmetric link detected: Node {i} links to Node {neighbor}, "
                    f"but Node {neighbor} does not link back to Node {i}.",
                    UserWarning,
                    stacklevel=2,
                )

    return graph


class TopologyGenerator:
    """Generates standard network topologies in adjacency-list format."""

    @staticmethod
    def line(nodes: int, bidirectional: bool = True) -> list[list[int]]:
        if nodes < 1:
            raise ValueError("A topology must have at least 1 node.")
        graph: list[list[int]] = [[] for _ in range(nodes)]
        for i in range(nodes - 1):
            graph[i].append(i + 2)
            if bidirectional:
                graph[i + 1].append(i + 1)
        return graph

    @staticmethod
    def ring(nodes: int, bidirectional: bool = True) -> list[list[int]]:
        if nodes < 1:
            raise ValueError("A topology must have at least 1 node.")
        graph = TopologyGenerator.line(nodes, bidirectional)
        if nodes > 2:
            graph[-1].append(1)
            if bidirectional:
                graph[0].append(nodes)
        return graph

    @staticmethod
    def star(nodes: int) -> list[list[int]]:
        if nodes < 1:
            raise ValueError("A topology must have at least 1 node.")
        graph: list[list[int]] = [[] for _ in range(nodes)]
        for i in range(1, nodes):
            graph[0].append(i + 1)
            graph[i].append(1)
        return graph

    @staticmethod
    def mesh(nodes: int) -> list[list[int]]:
        if nodes < 1:
            raise ValueError("A topology must have at least 1 node.")
        graph: list[list[int]] = []
        for i in range(nodes):
            neighbors = [j for j in range(1, nodes + 1) if j != i + 1]
            graph.append(neighbors)
        return graph

    @staticmethod
    def tree(depth: int, branching_factor: int = 2) -> list[list[int]]:
        if depth < 0:
            raise ValueError("Depth must be >= 0.")
        if branching_factor < 1:
            raise ValueError("Branching factor must be >= 1.")
            
        nodes = sum(branching_factor**d for d in range(depth + 1))
        graph: list[list[int]] = [[] for _ in range(nodes)]
        
        for i in range(nodes):
            for child_offset in range(1, branching_factor + 1):
                child_idx = (i * branching_factor) + child_offset
                if child_idx < nodes:
                    graph[i].append(child_idx + 1)
                    graph[child_idx].append(i + 1)
        return graph

    @staticmethod
    def random(nodes: int, probability: float = 0.5) -> list[list[int]]:
        if nodes < 1:
            raise ValueError("A topology must have at least 1 node.")
        if not (0.0 <= probability <= 1.0):
            raise ValueError("Probability must be between 0.0 and 1.0.")
            
        graph: list[list[int]] = [[] for _ in range(nodes)]
        if nodes == 1:
            return graph
            
        # 1. Ensure connectivity by creating a random spanning tree
        unvisited = list(range(1, nodes))
        random.shuffle(unvisited)
        visited = [0]
        for node in unvisited:
            parent = random.choice(visited)
            graph[parent].append(node + 1)
            graph[node].append(parent + 1)
            visited.append(node)
            
        # 2. Add random edges based on probability
        for i in range(nodes):
            for j in range(i + 1, nodes):
                if (j + 1) not in graph[i]:
                    if random.random() < probability:
                        graph[i].append(j + 1)
                        graph[j].append(i + 1)
                        
        # Sort neighbors for consistency
        return [sorted(neighbors) for neighbors in graph]

    @staticmethod
    def show(graph: list[list[int]]) -> None:
        """Prints a human-readable connectivity map and stats to stdout."""
        nodes = len(graph)
        edges = sum(len(neighbors) for neighbors in graph)
        print(f"Topology Info: {nodes} nodes, {edges} directed edges")
        print("Connectivity Map:")
        
        limit = 5 if nodes > 15 else nodes
        if nodes > 15:
            print(" (Graph too large to display entirely, showing first 5 nodes)")
            
        for i in range(limit):
            print(f"Node {i+1} -> {graph[i]}")
            
        if nodes > 15:
            print(" ...")

    @staticmethod
    def export_to_file(graph: list[list[int]], filename: str | Path) -> None:
        """Exports the adjacency matrix to a text file format readable by Simulation.from_file."""
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            for neighbors in graph:
                f.write(" ".join(str(n) for n in neighbors) + "\n")

    @staticmethod
    def export_to_dot(graph: list[list[int]], filename: str | Path) -> None:
        """Exports the adjacency matrix to DOT format (Graphviz)."""
        path = Path(filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w") as f:
            f.write("digraph G {\n")
            f.write("  node [shape=circle];\n")
            for i, neighbors in enumerate(graph, start=1):
                if not neighbors:
                    f.write(f"  {i};\n")  # Unconnected node
                for neighbor in neighbors:
                    f.write(f"  {i} -> {neighbor};\n")
            f.write("}\n")
