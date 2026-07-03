from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from modules.gymbrain.models.recommendations import Recommendation
from modules.gymbrain.providers.data_provider import DataProvider


@dataclass
class RuleResult:
    triggered: bool = False
    recommendation: Recommendation | None = None
    evidence: list[str] = field(default_factory=list)
    confidence: float = 0.0
    reason: str = ""


class BaseRule(ABC):
    """Abstract base for all GymBrain rules.

    Each rule encapsulates a single decision condition.
    Rules are modular, stateless, and independently testable.
    """

    def __init__(self, name: str, description: str = "", priority: int = 50) -> None:
        self._name = name
        self._description = description
        self._priority = priority

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def priority(self) -> int:
        return self._priority

    @abstractmethod
    def evaluate(self, provider: DataProvider, context: dict[str, Any] | None = None) -> RuleResult:
        """Evaluate the rule against the current data state.

        Returns a RuleResult that may or may not trigger a recommendation.
        """
