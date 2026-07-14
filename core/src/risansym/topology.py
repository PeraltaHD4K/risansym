from pathlib import Path

def load_adjacency_matrix(filename: str | Path) -> list[list[int]]:
    """Build the topology G=(V,E) from file, with format validation.

    Raises:
        FileNotFoundError: If the topology file does not exist.
        ValueError: If the file contains non-integer tokens or
            references nodes outside the valid range.
    """
    path = Path(filename)
    if not path.exists():
        raise FileNotFoundError(f"Topology file '{path}' does not exist.")

    graph: list[list[int]] = []
    line_idx = 0
    try:
        for line_idx, line in enumerate(path.read_text().splitlines()):
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

    # Validate that references do not point to out-of-range nodes
    num_nodes = len(graph)
    if num_nodes == 0:
        import warnings
        warnings.warn(
            f"Topology file '{path}' is empty. The simulation will have no nodes.",
            UserWarning,
            stacklevel=2,
        )

    for i, neighbors in enumerate(graph, start=1):
        for neighbor in neighbors:
            if neighbor < 1 or neighbor > num_nodes:
                raise ValueError(
                    f"Node {i} references node {neighbor}, which is outside "
                    f"the valid range (1 to {num_nodes})."
                )
            
            # Check for asymmetry
            if i not in graph[neighbor - 1]:
                import warnings
                warnings.warn(
                    f"Asymmetric link detected: Node {i} links to Node {neighbor}, "
                    f"but Node {neighbor} does not link back to Node {i}.",
                    UserWarning,
                    stacklevel=2,
                )

    return graph
