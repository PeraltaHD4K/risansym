"""Smoke-test an installed Risansym distribution without repository imports."""

from __future__ import annotations

from importlib.metadata import version
from importlib.resources import files

from risansym import Event, Model, ScheduleResult, Simulation


class Receiver(Model):
    """Minimal installed-package consumer."""

    received: list[str]

    def init(self) -> None:
        self.received = []

    def receive(self, event: Event) -> None:
        self.received.append(event.name)


def main() -> None:
    package_version = version("risansym")
    if package_version == "0.0.0-dev":
        raise RuntimeError("smoke test imported a source tree instead of the wheel")
    if not files("risansym").joinpath("py.typed").is_file():
        raise RuntimeError("installed wheel does not expose py.typed")

    receiver = Receiver()
    simulation = Simulation([[]], maxtime=1.0)
    simulation.set_model(receiver, 1)
    simulation.initialize_all()
    scheduled = simulation.seed_event(Event(0.0, "SMOKE", source=1, target=1))
    result = simulation.run()

    if scheduled is not ScheduleResult.SCHEDULED:
        raise RuntimeError(f"event was not scheduled: {scheduled}")
    if receiver.received != ["SMOKE"] or not result.complete:
        raise RuntimeError("installed simulation smoke test failed")
    print(f"smoke-tested risansym {package_version}")


if __name__ == "__main__":
    main()
