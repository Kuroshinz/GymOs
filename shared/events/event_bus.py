"""Typed event bus — wraps the core async EventBus with domain events."""

from __future__ import annotations

import logging
from typing import Callable

from core.event_bus import EventBus as CoreEventBus
from shared.events.event import DomainEvent

logger = logging.getLogger("nexus.events")

EventHandler = Callable[[DomainEvent], None]


class EventBus:
    """Typed wrapper around the core async EventBus.

    Provides a synchronous ``publish`` interface for domain events.
    Internally dispatches through the core async bus.
    """

    def __init__(self) -> None:
        self._core = CoreEventBus()
        self._handlers: dict[str, list[EventHandler]] = {}

    @property
    def core(self) -> CoreEventBus:
        return self._core

    def publish(self, event: DomainEvent) -> DomainEvent:
        """Publish a domain event synchronously."""
        event_name = event.event_name or event.__class__.__name__
        core_event = self._core.emit(
            event_name,
            data=event.to_dict(),
            source=event.source,
            correlation_id=event.correlation_id,
        )
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            if loop.is_running():
                asyncio.ensure_future(core_event)
            else:
                asyncio.run(core_event)
        except RuntimeError:
            asyncio.run(core_event)
        return event

    async def publish_async(self, event: DomainEvent) -> DomainEvent:
        """Publish a domain event asynchronously."""
        event_name = event.event_name or event.__class__.__name__
        await self._core.emit(
            event_name,
            data=event.to_dict(),
            source=event.source,
            correlation_id=event.correlation_id,
        )
        return event

    def subscribe(self, event_name: str, handler: EventHandler) -> None:
        """Subscribe a handler to a named event."""
        if event_name not in self._handlers:
            self._handlers[event_name] = []

            async def core_handler(core_event):
                payload = core_event.data or {}
                from shared.events.domain_events import event_from_dict
                try:
                    domain_event = event_from_dict(payload)
                except (ValueError, KeyError):
                    logger.warning("Could not deserialize event: %s", event_name)
                    return
                for h in self._handlers.get(event_name, []):
                    try:
                        h(domain_event)
                    except Exception:
                        logger.exception("Handler failed for %s", event_name)

            self._core.on(event_name, core_handler)

        self._handlers[event_name].append(handler)

    def subscribe_class(self, event_class: type[DomainEvent], handler: EventHandler) -> None:
        """Subscribe a handler to a domain event class."""
        self.subscribe(event_class.__name__, handler)

    def off(self, event_name: str, handler: EventHandler) -> None:
        """Remove a specific handler from an event."""
        handlers = self._handlers.get(event_name, [])
        if handler in handlers:
            handlers.remove(handler)
        if not handlers:
            self._core.off(event_name)
            self._handlers.pop(event_name, None)

    def clear(self) -> None:
        self._handlers.clear()
        self._core.clear()

    @property
    def handler_count(self) -> int:
        return sum(len(v) for v in self._handlers.values()) + self._core.handler_count


_bus_instance: EventBus | None = None


def get_event_bus() -> EventBus:
    global _bus_instance
    if _bus_instance is None:
        _bus_instance = EventBus()
    return _bus_instance
