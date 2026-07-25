from typing import Any

import pytest

from risansym.topology import TopologyGenerator


@pytest.mark.benchmark(group="topology")
def test_topology_random_1k(benchmark: Any) -> None:
    benchmark.pedantic(
        TopologyGenerator.random,
        args=(1_000, 0.01),
        kwargs={"seed": 42},
        iterations=5,
        rounds=3,
    )


@pytest.mark.benchmark(group="topology")
def test_topology_random_5k(benchmark: Any) -> None:
    benchmark.pedantic(
        TopologyGenerator.random,
        args=(5_000, 0.002),
        kwargs={"seed": 42},
        iterations=3,
        rounds=2,
    )


@pytest.mark.benchmark(group="topology")
def test_topology_random_10k(benchmark: Any) -> None:
    benchmark.pedantic(
        TopologyGenerator.random,
        args=(10_000, 0.001),
        kwargs={"seed": 42},
        iterations=1,
        rounds=1,
    )
