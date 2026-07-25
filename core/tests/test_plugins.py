"""Plugin manager contracts, ordering, contexts, and failure policies."""

from dataclasses import FrozenInstanceError

import pytest

from risansym.event import Event
from risansym.exceptions import (
    CausalityError,
    ConfigurationError,
    PluginError,
    TraceExportError,
)
from risansym.plugins.base import EngineContext, SimulationContext, SimulationPlugin
from risansym.plugins.manager import PluginFailurePolicy
from risansym.plugins.tracer import JSONTracerPlugin
from risansym.results import SimulationState
from risansym.simulation import Simulation


class RecordingPlugin(SimulationPlugin):
    def __init__(self, label: str, calls: list[str]) -> None:
        self.label = label
        self.calls = calls

    def on_start(self, context: SimulationContext) -> None:
        self.calls.append(f"{self.label}:start")

    def on_event_schedule(
        self,
        event: Event,
        context: EngineContext,
        node_state: dict[str, object] | None = None,
    ) -> Event:
        self.calls.append(f"{self.label}:schedule")
        return event

    def on_event_processed(
        self,
        event: Event,
        node_state: dict[str, object],
        context: EngineContext,
    ) -> None:
        self.calls.append(f"{self.label}:processed")

    def on_end(self, context: SimulationContext) -> None:
        self.calls.append(f"{self.label}:end")


def test_plugins_run_in_registration_order_and_lifecycle_only_once() -> None:
    calls: list[str] = []
    simulation = Simulation([[]], 10.0)
    simulation.attach(RecordingPlugin("first", calls))
    simulation.attach(RecordingPlugin("second", calls))
    simulation.initialize_all()
    simulation.seed_event(Event(time=1.0, source=1, target=1, name="ONE"))
    simulation.seed_event(Event(time=2.0, source=1, target=1, name="TWO"))

    simulation.step()
    simulation.run()

    assert calls == [
        "first:schedule",
        "second:schedule",
        "first:schedule",
        "second:schedule",
        "first:start",
        "second:start",
        "first:processed",
        "second:processed",
        "first:processed",
        "second:processed",
        "first:end",
        "second:end",
    ]


def test_plugin_contexts_are_immutable() -> None:
    captured: list[SimulationContext] = []

    class ContextPlugin(SimulationPlugin):
        def on_start(self, context: SimulationContext) -> None:
            captured.append(context)

    simulation = Simulation([[]], 10.0)
    simulation.attach(ContextPlugin())
    simulation.initialize_all()
    simulation.run()

    assert captured[0].state is SimulationState.RUNNING
    with pytest.raises(FrozenInstanceError):
        captured[0].topology = "changed"  # type: ignore[misc]


def test_raise_policy_preserves_plugin_failure_cause() -> None:
    class FailingPlugin(SimulationPlugin):
        def on_start(self, context: SimulationContext) -> None:
            raise ValueError("boom")

    simulation = Simulation([[]], 10.0)
    simulation.attach(FailingPlugin())
    simulation.initialize_all()

    with pytest.raises(PluginError, match="on_start") as captured:
        simulation.run()

    assert isinstance(captured.value.__cause__, ValueError)
    assert simulation.state is SimulationState.FAILED


def test_disable_policy_disables_plugin_after_first_failure() -> None:
    class FailingPlugin(SimulationPlugin):
        def __init__(self) -> None:
            self.calls = 0

        def on_event_schedule(
            self,
            event: Event,
            context: EngineContext,
            node_state: dict[str, object] | None = None,
        ) -> Event:
            self.calls += 1
            raise ValueError("boom")

    plugin = FailingPlugin()
    simulation = Simulation([[]], 10.0)
    simulation.attach(plugin, failure_policy=PluginFailurePolicy.DISABLE)
    simulation.initialize_all()
    simulation.seed_event(Event(time=1.0, source=1, target=1, name="ONE"))
    simulation.seed_event(Event(time=2.0, source=1, target=1, name="TWO"))

    assert plugin.calls == 1
    assert simulation.run().processed_events == 2


def test_transformed_event_is_revalidated_before_next_plugin() -> None:
    second_called = False

    class PastPlugin(SimulationPlugin):
        def on_event_schedule(self, event, context, node_state=None):
            return Event(time=1.0, source=1, target=1, name="PAST")

    class ObserverPlugin(SimulationPlugin):
        def on_event_schedule(self, event, context, node_state=None):
            nonlocal second_called
            second_called = True
            return event

    simulation = Simulation([[]], 10.0)
    simulation.attach(PastPlugin())
    simulation.attach(ObserverPlugin())
    simulation.initialize_all()
    simulation._runtime.clock = 2.0

    with pytest.raises(CausalityError):
        simulation.seed_event(Event(time=2.0, source=1, target=1, name="VALID"))
    assert not second_called


def test_disable_policy_isolates_invalid_transformation() -> None:
    class InvalidPlugin(SimulationPlugin):
        def on_event_schedule(self, event, context, node_state=None):
            return "not an event"

    simulation = Simulation([[]], 10.0)
    simulation.attach(
        InvalidPlugin(),
        failure_policy=PluginFailurePolicy.DISABLE,
    )
    simulation.initialize_all()

    simulation.seed_event(Event(time=1.0, source=1, target=1, name="ONE"))
    simulation.seed_event(Event(time=2.0, source=1, target=1, name="TWO"))

    assert simulation.run().processed_events == 2


def test_incomplete_non_plugin_object_is_rejected() -> None:
    simulation = Simulation([[]], 10.0)
    with pytest.raises(PluginError, match="SimulationPlugin"):
        simulation.attach(object())  # type: ignore[arg-type]


def test_trace_export_failure_is_critical(tmp_path) -> None:
    simulation = Simulation([[]], 10.0)
    simulation.attach(JSONTracerPlugin("FailureTest", trace_path=tmp_path))
    simulation.initialize_all()

    with pytest.raises(PluginError) as captured:
        simulation.run()

    assert isinstance(captured.value.__cause__, TraceExportError)
    assert simulation.state is SimulationState.FAILED


@pytest.mark.parametrize("algorithm", ["", "   ", None])
def test_tracer_requires_an_explicit_algorithm_name(algorithm: object) -> None:
    with pytest.raises(ConfigurationError, match="algorithm"):
        JSONTracerPlugin(algorithm)  # type: ignore[arg-type]
