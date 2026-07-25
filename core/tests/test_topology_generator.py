import tempfile
from pathlib import Path
import pytest
from risansym.topology import TopologyGenerator

def test_line_topology():
    graph = TopologyGenerator.line(4, bidirectional=True)
    assert len(graph) == 4
    assert graph[0] == [2]
    assert graph[1] == [1, 3]
    assert graph[2] == [2, 4]
    assert graph[3] == [3]

def test_line_unidirectional():
    graph = TopologyGenerator.line(3, bidirectional=False)
    assert graph[0] == [2]
    assert graph[1] == [3]
    assert graph[2] == []

def test_ring_topology():
    graph = TopologyGenerator.ring(4, bidirectional=True)
    assert len(graph) == 4
    assert graph[0] == [2, 4]
    assert graph[3] == [3, 1]

def test_star_topology():
    graph = TopologyGenerator.star(5)
    assert len(graph) == 5
    assert set(graph[0]) == {2, 3, 4, 5}
    for i in range(1, 5):
        assert graph[i] == [1]

def test_mesh_topology():
    graph = TopologyGenerator.mesh(4)
    assert len(graph) == 4
    for i in range(4):
        assert len(graph[i]) == 3
        assert (i + 1) not in graph[i]

def test_tree_topology():
    graph = TopologyGenerator.tree(depth=2, branching_factor=2)
    # Depth 2 binary tree: 1 + 2 + 4 = 7 nodes
    assert len(graph) == 7
    # Root
    assert set(graph[0]) == {2, 3}
    # Level 1
    assert set(graph[1]) == {4, 5, 1}
    assert set(graph[2]) == {6, 7, 1}
    # Level 2 (Leaves)
    assert graph[3] == [2]
    assert graph[6] == [3]

def test_random_topology():
    graph = TopologyGenerator.random(10, probability=0.5)
    assert len(graph) == 10
    # Graph should be connected, so at least 9 edges (18 directed)
    edges = sum(len(n) for n in graph)
    assert edges >= 18

def test_export_to_file():
    graph = TopologyGenerator.ring(3)
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "topo.txt"
        TopologyGenerator.export_to_file(graph, filepath)
        content = filepath.read_text().splitlines()
        assert len(content) == 3
        assert content[0] == "2 3"
        assert content[1] == "1 3"
        assert content[2] == "2 1"
