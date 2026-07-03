"""Base subscriber — modules extend this to react to domain events."""

from abc import ABC, abstractmethod
from typing import Any

from shared.events.domain_events import DomainEvent
from shared.events.event_bus import EventBus, get_event_bus


class Subscriber(ABC):
    """Base class for event subscribers.

    Subclasses define which events they handle via ``handled_events()``
    and implement ``handle(event)``.
    """

    def __init__(self, bus: EventBus | None = None) -> None:
        self._bus = bus or get_event_bus()
        self._register()

    def _register(self) -> None:
        for event_class in self.handled_events():
            event_name = getattr(event_class, "__name__", str(event_class))
            self._bus.subscribe(event_name, self._wrap_handle)

    def _wrap_handle(self, event: DomainEvent) -> None:
        self.handle(event)

    @abstractmethod
    def handled_events(self) -> list[type[DomainEvent]]:
        """Return the list of domain event classes this subscriber handles."""
        ...

    @abstractmethod
    def handle(self, event: DomainEvent) -> None:
        """React to a domain event."""
        ...

    @property
    def bus(self) -> EventBus:
        return self._bus
