"""Base publisher — modules extend this to publish domain events."""

from typing import TypeVar

from shared.events.domain_events import DomainEvent
from shared.events.event_bus import EventBus, get_event_bus

E = TypeVar("E", bound=DomainEvent)


class Publisher:
    """Base class for event publishers.

    Modules that publish domain events should inherit from this class
    and call ``self.publish(event)``.
    """

    def __init__(self, bus: EventBus | None = None) -> None:
        self._bus = bus or get_event_bus()

    def publish(self, event: E) -> E:
        self._bus.publish(event)
        return event

    @property
    def bus(self) -> EventBus:
        return self._bus
