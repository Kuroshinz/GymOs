from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger("runtime.context")


@dataclass
class RuntimeContext:
    collected_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    capabilities: dict = field(default_factory=dict)
    kernel: dict = field(default_factory=dict)
    knowledge_graph: dict = field(default_factory=dict)
    prediction: dict = field(default_factory=dict)
    recovery: dict = field(default_factory=dict)
    planning: dict = field(default_factory=dict)
    adaptive: dict = field(default_factory=dict)
    intent: dict = field(default_factory=dict)
    product_state: dict = field(default_factory=dict)
    nutrition: dict = field(default_factory=dict)
    workout: dict = field(default_factory=dict)

    errors: list[str] = field(default_factory=list)

    @property
    def sections(self) -> list[str]:
        return [
            "capabilities", "kernel", "knowledge_graph", "prediction",
            "recovery", "planning", "adaptive", "intent", "product_state",
            "nutrition", "workout",
        ]

    @property
    def available_sections(self) -> list[str]:
        return [s for s in self.sections if self._section_has_data(s)]

    def _section_has_data(self, section: str) -> bool:
        data = getattr(self, section, {})
        return isinstance(data, dict) and len(data) > 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "collected_at": self.collected_at,
            "sections": {s: getattr(self, s, {}) for s in self.sections},
            "errors": self.errors,
        }

    def merge(self, other: RuntimeContext) -> None:
        for section in self.sections:
            other_data = getattr(other, section, {})
            if other_data:
                setattr(self, section, other_data)
        self.errors.extend(other.errors)
        self.collected_at = other.collected_at


SectionProvider = Any


class ContextCollector:
    def __init__(self) -> None:
        self._providers: dict[str, SectionProvider] = {}

    def register_provider(self, section: str, provider: SectionProvider) -> None:
        self._providers[section] = provider

    def unregister_provider(self, section: str) -> None:
        self._providers.pop(section, None)

    async def collect(self) -> RuntimeContext:
        context = RuntimeContext()
        for section, provider in self._providers.items():
            try:
                data = await self._call_provider(provider)
                if data is not None:
                    setattr(context, section, data)
            except Exception as exc:
                logger.warning("Context provider '%s' failed: %s", section, exc)
                context.errors.append(f"{section}: {exc}")
        return context

    async def collect_section(self, section: str) -> dict:
        provider = self._providers.get(section)
        if provider is None:
            return {}
        try:
            data = await self._call_provider(provider)
            return data or {}
        except Exception as exc:
            logger.warning("Context section '%s' failed: %s", section, exc)
            return {"error": str(exc)}

    async def _call_provider(self, provider: SectionProvider) -> Any:
        if callable(provider):
            result = provider()
            if hasattr(result, "__await__"):
                result = await result
            return result
        return provider

    @property
    def registered_sections(self) -> list[str]:
        return list(self._providers.keys())
