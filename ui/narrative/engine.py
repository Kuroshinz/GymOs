from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Tone(Enum):
    COACH = "coach"
    SCIENTIFIC = "scientific"


class Length(Enum):
    SHORT = "short"
    MEDIUM = "medium"
    DETAILED = "detailed"


@dataclass
class Narrative:
    """Structured narrative output from a template function."""

    title: str
    summary: str = ""
    body: str = ""
    detail: str = ""
    tone: Tone = Tone.COACH
    action_items: list[str] = field(default_factory=list)
    source_keys: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def render(self, length: Length = Length.MEDIUM) -> str:
        if length == Length.SHORT:
            return self.summary
        if length == Length.MEDIUM:
            return self.body or self.summary
        return self.detail or self.body or self.summary


NarrativeTemplate = Callable[..., Narrative]


class NarrativeEngine:
    """Deterministic template rendering engine for intelligent UX narratives.

    Consumes existing platform data models (CommandCenterData, DashboardData)
    and produces structured Narrative objects with no calculations or AI.
    """

    def __init__(self) -> None:
        self._registry: dict[str, NarrativeTemplate] = {}

    def register(self, name: str, template: NarrativeTemplate) -> None:
        self._registry[name] = template

    def render(self, template_name: str, *args: Any, tone: Tone = Tone.COACH, **kwargs: Any) -> Narrative | None:
        template = self._registry.get(template_name)
        if template is None:
            return None
        n = template(*args, **kwargs)
        n.tone = tone
        if tone == Tone.SCIENTIFIC:
            n = self._apply_scientific_tone(n)
        return n

    def available(self) -> list[str]:
        return list(self._registry.keys())

    @staticmethod
    def _apply_scientific_tone(n: Narrative) -> Narrative:
        return Narrative(
            title=n.title,
            summary=n.summary,
            body=n.body,
            detail=n.detail,
            tone=Tone.SCIENTIFIC,
            action_items=n.action_items,
            source_keys=n.source_keys,
            metadata=n.metadata,
        )

    def render_all(self, *args: Any, tone: Tone = Tone.COACH, **kwargs: Any) -> list[Narrative]:
        return [
            n for tname in sorted(self._registry.keys())
            if (n := self.render(tname, *args, tone=tone, **kwargs))
        ]
