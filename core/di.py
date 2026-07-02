from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable, TypeVar

T = TypeVar("T")


class ServiceLifetime(Enum):
    SINGLETON = "singleton"
    TRANSIENT = "transient"


class ServiceDescriptor:
    def __init__(
        self,
        name: str,
        factory: Callable[[], Any],
        lifetime: ServiceLifetime = ServiceLifetime.SINGLETON,
    ) -> None:
        self.name = name
        self.factory = factory
        self.lifetime = lifetime
        self._instance: Any = None

    def resolve(self) -> Any:
        if self.lifetime == ServiceLifetime.SINGLETON:
            if self._instance is None:
                self._instance = self.factory()
            return self._instance
        return self.factory()


class Disposable(ABC):
    @abstractmethod
    async def dispose(self) -> None: ...


class Container:
    def __init__(self) -> None:
        self._services: dict[str, ServiceDescriptor] = {}
        self._aliases: dict[str, str] = {}

    def register(
        self,
        name: str,
        instance: Any,
    ) -> None:
        desc = ServiceDescriptor(
            name=name, factory=lambda: instance, lifetime=ServiceLifetime.SINGLETON
        )
        desc._instance = instance
        self._services[name] = desc

    def register_factory(
        self,
        name: str,
        factory: Callable[[], Any],
        lifetime: ServiceLifetime = ServiceLifetime.SINGLETON,
    ) -> None:
        self._services[name] = ServiceDescriptor(
            name=name, factory=factory, lifetime=lifetime
        )

    def alias(self, alias: str, target: str) -> None:
        self._aliases[alias] = target

    def resolve(self, name: str) -> Any:
        resolved_name = self._aliases.get(name, name)
        descriptor = self._services.get(resolved_name)
        if descriptor is None:
            raise KeyError(f"Service '{name}' not registered")
        return descriptor.resolve()

    def get(self, klass: type[T]) -> T:
        name = klass.__name__
        return self.resolve(name)

    def has(self, name: str) -> bool:
        resolved_name = self._aliases.get(name, name)
        return resolved_name in self._services

    async def dispose(self) -> None:
        for descriptor in self._services.values():
            instance = descriptor._instance
            if instance is not None:
                dispose_fn = getattr(instance, "dispose", None)
                if dispose_fn is not None:
                    try:
                        result = dispose_fn()
                        if hasattr(result, "__await__"):
                            await result
                    except Exception:
                        pass
        self._services.clear()
        self._aliases.clear()
