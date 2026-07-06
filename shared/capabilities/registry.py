"""Capability Registry — central store of all GymOS capabilities.

Populated at import time with static capability definitions.
Thread-safe read-only access after initialization.
"""

from __future__ import annotations

from collections.abc import Iterator

from shared.capabilities.capability import Capability


class CapabilityRegistry:
    """Registry of all platform capabilities.

    Usage:
        registry = CapabilityRegistry.get_instance()
        training = registry.find("training_intelligence")
        all_caps = registry.list_all()
    """

    _instance: CapabilityRegistry | None = None

    def __init__(self) -> None:
        if CapabilityRegistry._instance is not None:
            msg = "CapabilityRegistry is a singleton. Use CapabilityRegistry.get_instance()"
            raise RuntimeError(msg)
        self._capabilities: dict[str, Capability] = {}
        self._frozen = False

    @classmethod
    def get_instance(cls) -> CapabilityRegistry:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register(self, capability: Capability) -> None:
        if self._frozen:
            msg = "Cannot register capabilities after initialization"
            raise RuntimeError(msg)
        if capability.capability_id in self._capabilities:
            msg = f"Capability '{capability.capability_id}' is already registered"
            raise ValueError(msg)
        self._capabilities[capability.capability_id] = capability

    def freeze(self) -> None:
        """Lock the registry after all capabilities are registered."""
        self._frozen = True

    @property
    def is_frozen(self) -> bool:
        return self._frozen

    def find(self, capability_id: str) -> Capability | None:
        return self._capabilities.get(capability_id)

    def search(self, query: str) -> list[Capability]:
        q = query.lower()
        return [
            cap for cap in self._capabilities.values()
            if q in cap.name.lower() or q in cap.description.lower() or q in cap.capability_id.lower()
        ]

    def list_all(self) -> list[Capability]:
        return list(self._capabilities.values())

    def list_by_category(self, category: str) -> list[Capability]:
        return [cap for cap in self._capabilities.values() if cap.category == category]

    def __iter__(self) -> Iterator[Capability]:
        return iter(self._capabilities.values())

    def __len__(self) -> int:
        return len(self._capabilities)

    def __contains__(self, capability_id: str) -> bool:
        return capability_id in self._capabilities
