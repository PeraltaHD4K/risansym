"""Tests for deterministic topology generation and export."""

import random
from pathlib import Path

import pytest

from risansym.exceptions import ConfigurationError
from risansym.topology import TopologyGenerator


def test_line_topology() -> None:
    assert TopologyGenerator.line(4) == [[2], [1, 3], [2, 4], [3]]
    assert TopologyGenerator.line(3, directed=True) == [[2], [3], []]


def test_ring_topology() -> None:
    assert TopologyGenerator.ring(4) == [[2, 4], [1, 3], [2, 4], [1, 3]]
    assert TopologyGenerator.ring(4, directed=True) == [[2], [3], [4], [1]]


def test_star_topology() -> None:
    assert TopologyGenerator.star(4) == [[2, 3, 4], [1], [1], [1]]
    assert TopologyGenerator.star(4, directed=True) == [[2, 3, 4], [], [], []]


def test_mesh_topology() -> None:
    graph = TopologyGenerator.mesh(4)
    assert all(len(neighbors) == 3 for neighbors in graph)
    assert all(node_id not in graph[node_id - 1] for node_id in range(1, 5))


def test_tree_topology() -> None:
    graph = TopologyGenerator.tree(depth=2, branching_factor=2)
    assert len(graph) == 7
    assert set(graph[0]) == {2, 3}
    assert set(graph[1]) == {1, 4, 5}
    assert set(graph[2]) == {1, 6, 7}


def test_random_topology_is_reproducible_with_seed() -> None:
    first = TopologyGenerator.random(20, probability=0.2, seed=42)
    second = TopologyGenerator.random(20, probability=0.2, seed=42)
    different = TopologyGenerator.random(20, probability=0.2, seed=43)

    assert first == second
    assert first != different


def test_random_topology_accepts_explicit_rng() -> None:
    assert TopologyGenerator.random(10, rng=random.Random(7)) == (
        TopologyGenerator.random(10, rng=random.Random(7))
    )


def test_random_topology_rejects_seed_and_rng() -> None:
    with pytest.raises(ConfigurationError, match="either seed or rng"):
        TopologyGenerator.random(10, seed=1, rng=random.Random(1))


def test_export_adjacency_list(tmp_path: Path) -> None:
    path = tmp_path / "topology.txt"
    TopologyGenerator.export_adjacency_list(TopologyGenerator.ring(3), path)
    assert path.read_text(encoding="utf-8").splitlines() == ["2 3", "1 3", "1 2"]


def test_export_dot_respects_direction(tmp_path: Path) -> None:
    path = tmp_path / "topology.dot"
    TopologyGenerator.export_dot([[2], []], path, directed=True)
    content = path.read_text(encoding="utf-8")
    assert content.startswith("digraph G")
    assert "1 -> 2;" in content
