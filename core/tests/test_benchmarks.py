import pytest
from risansym.topology import TopologyGenerator

@pytest.mark.benchmark(group="topology")
def test_topology_random_1k(benchmark):
    benchmark.pedantic(TopologyGenerator.random, args=(1000, 0.01), iterations=5, rounds=3)

@pytest.mark.benchmark(group="topology")
def test_topology_random_5k(benchmark):
    benchmark.pedantic(TopologyGenerator.random, args=(5000, 0.002), iterations=3, rounds=2)

@pytest.mark.benchmark(group="topology")
def test_topology_random_10k(benchmark):
    # Just measure 10k nodes (PERF-03)
    benchmark.pedantic(TopologyGenerator.random, args=(10000, 0.001), iterations=1, rounds=1)
