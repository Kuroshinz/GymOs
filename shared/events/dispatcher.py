"""Event dispatcher — auto-discovers and registers subscribers."""

from __future__ import annotations

import logging
import pkgutil
from importlib import import_module
from pathlib import Path

from shared.events.event_bus import EventBus, get_event_bus
from shared.events.subscriber import Subscriber

logger = logging.getLogger("nexus.events.dispatcher")


def discover_subscribers(package_path: str = "shared.events.subscribers") -> list[type[Subscriber]]:
    """Auto-discover all Subscriber classes in a package."""
    subscribers: list[type[Subscriber]] = []
    try:
        package = import_module(package_path)
    except ImportError:
        return subscribers

    package_path_obj = Path(package.__path__[0]) if hasattr(package, "__path__") else None
    if not package_path_obj or not package_path_obj.exists():
        return subscribers

    for _, name, _ in pkgutil.iter_modules([str(package_path_obj)]):
        try:
            module = import_module(f"{package_path}.{name}")
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, Subscriber)
                    and attr is not Subscriber
                ):
                    subscribers.append(attr)
        except Exception as exc:
            logger.warning("Failed to load subscriber module %s: %s", name, exc)

    return subscribers


def register_subscribers(
    bus: EventBus | None = None,
    subscriber_classes: list[type[Subscriber]] | None = None,
) -> list[Subscriber]:
    """Register all discovered or provided subscriber classes with the bus."""
    bus = bus or get_event_bus()
    instances: list[Subscriber] = []

    if subscriber_classes is None:
        subscriber_classes = discover_subscribers()

    for cls in subscriber_classes:
        try:
            instance = cls(bus=bus)
            instances.append(instance)
            logger.info("Registered subscriber: %s", cls.__name__)
        except Exception as exc:
            logger.error("Failed to register subscriber %s: %s", cls.__name__, exc)

    return instances
