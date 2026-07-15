import pytest

@pytest.fixture
def temp_topology(tmp_path):
    """Creates a temporary 2-node topology file for tests."""
    topo_file = tmp_path / "topo.txt"
    topo_file.write_text("2\n1\n")
    return topo_file
