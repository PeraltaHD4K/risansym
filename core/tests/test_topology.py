"""Tests for topology normalization, loading, and Simulation integration."""

from pathlib import Path

import pytest

from risansym.exceptions import TopologyError
from risansym.simulation import Simulation
from risansym.topology import (
    load_adjacency_list,
    load_dense_matrix,
    load_edge_list,
    normalize_topology,
)


@pytest.fixture
def make_topology(tmp_path: Path):
    """Return a factory that writes one topology fixture."""

    def make(content: str) -> Path:
        topology_file = tmp_path / "topology.txt"
        topology_file.write_text(content, encoding="utf-8")
        return topology_file

    return make


class TestTopologyNormalization:
    def test_copies_valid_undirected_topology(self) -> None:
        source = [[2], [1]]
        normalized = normalize_topology(source, directed=False)

        assert normalized == source
        assert normalized is not source
        assert normalized[0] is not source[0]

    def test_accepts_asymmetry_only_for_directed_topology(self) -> None:
        assert normalize_topology([[2], []], directed=True) == [[2], []]
        with pytest.raises(TopologyError, match="asymmetric"):
            normalize_topology([[2], []], directed=False)

    @pytest.mark.parametrize(
        ("graph", "message"),
        [
            ([], "at least one node"),
            ([[0]], "outside the valid range"),
            ([[-1]], "outside the valid range"),
            ([[2, 2], [1]], "duplicate neighbor"),
            ([[1]], "self-loop"),
            ([[True]], "non-integer neighbor"),
        ],
    )
    def test_rejects_invalid_graphs(
        self,
        graph: list[list[int]],
        message: str,
    ) -> None:
        with pytest.raises(TopologyError, match=message):
            normalize_topology(graph, directed=True)

    def test_simulation_validates_direct_graph_input(self) -> None:
        with pytest.raises(TopologyError, match="outside the valid range"):
            Simulation([[99]], maxtime=10.0)


class TestAdjacencyListLoader:
    def test_loads_valid_undirected_topology(self, make_topology) -> None:
        path = make_topology("2\n1\n")
        assert load_adjacency_list(path) == [[2], [1]]

    def test_blank_rows_represent_isolated_nodes(self, make_topology) -> None:
        path = make_topology("\n\n")
        assert load_adjacency_list(path) == [[], []]

    def test_comments_do_not_create_nodes(self, make_topology) -> None:
        path = make_topology("# two nodes\n2\n# reciprocal edge\n1\n")
        assert load_adjacency_list(path) == [[2], [1]]

    def test_rejects_non_integer_neighbor(self, make_topology) -> None:
        path = make_topology("2\ninvalid\n")
        with pytest.raises(TopologyError, match="neighbors must be integers"):
            load_adjacency_list(path)

    def test_rejects_empty_file(self, make_topology) -> None:
        path = make_topology("")
        with pytest.raises(TopologyError, match="at least one node"):
            load_adjacency_list(path)


class TestEdgeListLoader:
    def test_loads_undirected_edges_and_preserves_isolated_nodes(
        self,
        make_topology,
    ) -> None:
        path = make_topology("1 2\n")
        assert load_edge_list(path, node_count=3) == [[2], [1], []]

    def test_loads_directed_edges(self, make_topology) -> None:
        path = make_topology("1 2\n2 3\n3 1\n")
        assert load_edge_list(path, directed=True) == [[2], [3], [1]]

    @pytest.mark.parametrize("content", ["0 1\n", "-1 2\n", "1 0\n"])
    def test_rejects_non_positive_node_ids(self, make_topology, content: str) -> None:
        path = make_topology(content)
        with pytest.raises(TopologyError, match="must be positive"):
            load_edge_list(path)

    def test_rejects_invalid_column_count(self, make_topology) -> None:
        path = make_topology("1 2 3\n")
        with pytest.raises(TopologyError, match="exactly two integers"):
            load_edge_list(path)

    def test_rejects_duplicate_edges(self, make_topology) -> None:
        path = make_topology("1 2\n1 2\n")
        with pytest.raises(TopologyError, match="duplicate neighbor"):
            load_edge_list(path, directed=True)

    def test_empty_edge_list_requires_node_count(self, make_topology) -> None:
        path = make_topology("# no edges\n")
        with pytest.raises(TopologyError, match="requires a positive node_count"):
            load_edge_list(path)
        assert load_edge_list(path, node_count=2) == [[], []]


class TestDenseMatrixLoader:
    def test_loads_directed_matrix(self, make_topology) -> None:
        path = make_topology("0 1 0\n0 0 1\n1 0 0\n")
        assert load_dense_matrix(path, directed=True) == [[2], [3], [1]]

    def test_rejects_non_binary_values(self, make_topology) -> None:
        path = make_topology("0 2\n1 0\n")
        with pytest.raises(TopologyError, match="must be 0 or 1"):
            load_dense_matrix(path)

    @pytest.mark.parametrize(
        "content",
        [
            "0 1 0\n1 0\n0 0 0 0\n",
            "0 1\n1 0\n0 0\n",
        ],
    )
    def test_rejects_non_square_matrix(self, make_topology, content: str) -> None:
        path = make_topology(content)
        with pytest.raises(TopologyError, match="must be square"):
            load_dense_matrix(path, directed=True)


class TestSimulationTopologyFiles:
    def test_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            Simulation.from_file(tmp_path / "missing.txt", maxtime=10.0)

    def test_directory_is_rejected(self, tmp_path: Path) -> None:
        with pytest.raises(IsADirectoryError):
            Simulation.from_file(tmp_path, maxtime=10.0)

    def test_topology_name_comes_from_file(self, make_topology) -> None:
        path = make_topology("2\n1\n")
        simulation = Simulation.from_file(path, maxtime=10.0)
        assert simulation.graph == [[2], [1]]
        assert "topology" in repr(simulation)

    def test_edge_list_node_count_is_available_from_simulation(self, make_topology) -> None:
        path = make_topology("1 2\n")
        simulation = Simulation.from_file(
            path,
            maxtime=10.0,
            format="edge_list",
            node_count=3,
        )
        assert simulation.graph == [[2], [1], []]
