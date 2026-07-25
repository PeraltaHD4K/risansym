"""Plugin registration, validation, dispatch, and failure isolation."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from functools import partial
from typing import Callable, TypeVar

from risansym.event import Event, JsonPayload
from risansym.exceptions import PluginError
from risansym.plugins.base import EngineContext, SimulationContext, SimulationPlugin

logger = logging.getLogger(__name__)
T = TypeVar("T")


class PluginFailurePolicy(Enum):
    """Behavior when a plugin callback raises an exception."""

    RAISE = "raise"
    LOG = "log"
    DISABLE = "disable"


@dataclass(slots=True)
class _PluginRegistration:
    plugin: SimulationPlugin
    policy: PluginFailurePolicy
    enabled: bool = True


class PluginManager:
    """Own and invoke plugins in deterministic registration order."""

    def __init__(self, default_policy: PluginFailurePolicy = PluginFailurePolicy.RAISE) -> None:
        if not isinstance(default_policy, PluginFailurePolicy):
            raise PluginError("default plugin policy must be a PluginFailurePolicy.")
        self._default_policy = default_policy
        self._registrations: list[_PluginRegistration] = []

    @property
    def plugins(self) -> tuple[SimulationPlugin, ...]:
        """Registered plugins as a read-only tuple."""
        return tuple(registration.plugin for registration in self._registrations)

    @property
    def requires_state_snapshot(self) -> bool:
        """Whether an enabled plugin requests model snapshots."""
        return any(
            registration.enabled and registration.plugin.requires_state_snapshot
            for registration in self._registrations
        )

    def attach(
        self,
        plugin: SimulationPlugin,
        *,
        policy: PluginFailurePolicy | None = None,
    ) -> None:
        """Validate and register one plugin."""
        if not isinstance(plugin, SimulationPlugin):
            raise PluginError(f"Expected a SimulationPlugin instance, got {type(plugin).__name__}.")
        selected_policy = self._default_policy if policy is None else policy
        if not isinstance(selected_policy, PluginFailurePolicy):
            raise PluginError("plugin policy must be a PluginFailurePolicy.")
        self._registrations.append(_PluginRegistration(plugin, selected_policy))

    def _invoke(
        self,
        registration: _PluginRegistration,
        callback_name: str,
        callback: Callable[[], T],
        fallback: T,
    ) -> T:
        try:
            return callback()
        except Exception as error:
            plugin_name = type(registration.plugin).__name__
            if registration.policy is PluginFailurePolicy.RAISE:
                raise PluginError(
                    f"Plugin {plugin_name} failed during {callback_name}: {error}"
                ) from error
            logger.exception("Plugin %s failed during %s.", plugin_name, callback_name)
            if registration.policy is PluginFailurePolicy.DISABLE:
                registration.enabled = False
            return fallback

    def notify_start(self, context: SimulationContext) -> None:
        for registration in self._registrations:
            if registration.enabled:
                self._invoke(
                    registration,
                    "on_start",
                    partial(registration.plugin.on_start, context),
                    None,
                )

    def transform_scheduled_event(
        self,
        event: Event,
        context: EngineContext,
        node_state: JsonPayload | None,
        validator: Callable[[object], Event],
    ) -> Event | None:
        transformed: Event | None = event
        for registration in self._registrations:
            if not registration.enabled or transformed is None:
                continue
            current = transformed
            fallback: Event | None = current
            transformed = self._invoke(
                registration,
                "on_event_schedule",
                partial(
                    registration.plugin.on_event_schedule,
                    current,
                    context,
                    node_state,
                ),
                fallback,
            )
            if transformed is not None:
                try:
                    transformed = validator(transformed)
                except Exception:
                    if registration.policy is PluginFailurePolicy.RAISE:
                        raise
                    logger.exception(
                        "Plugin %s returned an invalid event during on_event_schedule.",
                        type(registration.plugin).__name__,
                    )
                    if registration.policy is PluginFailurePolicy.DISABLE:
                        registration.enabled = False
                    transformed = current
                if transformed.time > context.maxtime:
                    break
        return transformed

    def notify_event_processed(
        self,
        event: Event,
        node_state: JsonPayload,
        context: EngineContext,
    ) -> None:
        for registration in self._registrations:
            if registration.enabled:
                self._invoke(
                    registration,
                    "on_event_processed",
                    partial(registration.plugin.on_event_processed, event, node_state, context),
                    None,
                )

    def notify_app_log(
        self,
        source: int,
        message: str,
        context: EngineContext,
    ) -> None:
        for registration in self._registrations:
            if registration.enabled:
                self._invoke(
                    registration,
                    "on_app_log",
                    partial(registration.plugin.on_app_log, source, message, context),
                    None,
                )

    def notify_end(self, context: SimulationContext) -> None:
        for registration in self._registrations:
            if registration.enabled:
                self._invoke(
                    registration,
                    "on_end",
                    partial(registration.plugin.on_end, context),
                    None,
                )
