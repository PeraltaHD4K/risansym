"""Tests for topology loading and validation in Simulation."""

import pytest
from pathlib import Path
from risansym.simulation import Simulation


@pytest.fixture
def make_topo(tmp_path):
    """Factory fixture that writes a topology file and returns its path."""
    def _make(content: str) -> Path:
        topo_file = tmp_path / "topo.txt"
        topo_file.write_text(content)
        return topo_file
    return _make


class TestTopologyValidation:
    def test_file_not_found_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="does not exist"):
            Simulation.from_file(filename=tmp_path / "nonexistent.txt", maxtime=10.0, trace_network=False, app_logs=False)

    def test_non_integer_token_raises(self, make_topo):
        topo = make_topo("2\nabc\n")
        with pytest.raises(ValueError, match="must be integers"):
            Simulation.from_file(filename=topo, maxtime=10.0, trace_network=False, app_logs=False)

    def test_out_of_range_neighbor_raises(self, make_topo):
        # 2 nodes, but node 1 references node 99
        topo = make_topo("99\n1\n")
        with pytest.raises(ValueError, match="outside the valid range"):
            Simulation.from_file(filename=topo, maxtime=10.0, trace_network=False, app_logs=False)

    def test_valid_topology_loads(self, make_topo):
        topo = make_topo("2\n1\n")
        sim = Simulation.from_file(filename=topo, maxtime=10.0, trace_network=False, app_logs=False)
        assert len(sim.graph) == 2
        assert sim.graph[0] == [2]
        assert sim.graph[1] == [1]

    def test_empty_lines_are_skipped(self, make_topo):
        topo = make_topo("\n2\n\n1\n\n")
        sim = Simulation.from_file(filename=topo, maxtime=10.0, trace_network=False, app_logs=False)
        assert len(sim.graph) == 2

    def test_set_model_invalid_node_raises(self, make_topo):
        from risansym.model import Model

        class Dummy(Model):
            def init(self): pass
            def receive(self, event): pass

        topo = make_topo("2\n1\n")
        sim = Simulation.from_file(filename=topo, maxtime=10.0, trace_network=False, app_logs=False)

        with pytest.raises(IndexError, match="does not exist"):
            sim.set_model(Dummy(), node_id=99)

        with pytest.raises(IndexError, match="does not exist"):
            sim.set_model(Dummy(), node_id=0)

    def test_empty_topology_warning(self, make_topo):
        # T6: Empty topology
        topo = make_topo("")
        with pytest.warns(UserWarning, match="is empty. The simulation will have no nodes"):
            sim = Simulation.from_file(filename=topo, maxtime=10.0, trace_network=False, app_logs=False)
        assert len(sim.graph) == 0

    def test_directory_path_raises(self, tmp_path):
        # T7: Directory path instead of file
        with pytest.raises(IsADirectoryError):
            Simulation.from_file(filename=tmp_path, maxtime=10.0, trace_network=False, app_logs=False)

    def test_load_edge_list(self, make_topo):
        topo = make_topo("1 2\n2 3\n3 1\n")
        sim = Simulation.from_file(filename=topo, maxtime=10.0, format="edge_list", trace_network=False, app_logs=False)
        assert len(sim.graph) == 3
        assert sim.graph[0] == [2]
        assert sim.graph[1] == [3]
        assert sim.graph[2] == [1]

    def test_load_dense_matrix(self, make_topo):
        topo = make_topo("0 1 0\n0 0 1\n1 0 0\n")
        sim = Simulation.from_file(filename=topo, maxtime=10.0, format="dense_matrix", trace_network=False, app_logs=False)
        assert len(sim.graph) == 3
        assert sim.graph[0] == [2]
        assert sim.graph[1] == [3]
        assert sim.graph[2] == [1]

    def test_load_dense_matrix_invalid_value(self, make_topo):
        topo = make_topo("0 2 0\n")
        with pytest.raises(ValueError, match="Matrix cells must be 0 or 1"):
            Simulation.from_file(filename=topo, maxtime=10.0, format="dense_matrix", trace_network=False, app_logs=False)

    def test_load_edge_list_invalid_format(self, make_topo):
        topo = make_topo("1 2 3\n")
        with pytest.raises(ValueError, match="exactly 2 integers"):
            Simulation.from_file(filename=topo, maxtime=10.0, format="edge_list", trace_network=False, app_logs=False)
