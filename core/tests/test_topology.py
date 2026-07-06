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
            Simulation.from_file(filename=tmp_path / "nonexistent.txt", maxtime=10.0, debug=False)

    def test_non_integer_token_raises(self, make_topo):
        topo = make_topo("2\nabc\n")
        with pytest.raises(ValueError, match="must be integers"):
            Simulation.from_file(filename=topo, maxtime=10.0, debug=False)

    def test_out_of_range_neighbor_raises(self, make_topo):
        # 2 nodes, but node 1 references node 99
        topo = make_topo("99\n1\n")
        with pytest.raises(ValueError, match="outside the valid range"):
            Simulation.from_file(filename=topo, maxtime=10.0, debug=False)

    def test_valid_topology_loads(self, make_topo):
        topo = make_topo("2\n1\n")
        sim = Simulation.from_file(filename=topo, maxtime=10.0, debug=False)
        assert len(sim.graph) == 2
        assert sim.graph[0] == [2]
        assert sim.graph[1] == [1]

    def test_empty_lines_are_skipped(self, make_topo):
        topo = make_topo("\n2\n\n1\n\n")
        sim = Simulation.from_file(filename=topo, maxtime=10.0, debug=False)
        assert len(sim.graph) == 2

    def test_set_model_invalid_node_raises(self, make_topo):
        from risansym.model import Model

        class Dummy(Model):
            def init(self): pass
            def receive(self, event): pass

        topo = make_topo("2\n1\n")
        sim = Simulation.from_file(filename=topo, maxtime=10.0, debug=False)

        with pytest.raises(IndexError, match="does not exist"):
            sim.set_model(Dummy(), node_id=99)

        with pytest.raises(IndexError, match="does not exist"):
            sim.set_model(Dummy(), node_id=0)
