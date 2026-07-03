from __future__ import annotations

from typing import Any

from modules.gymbrain.models.recommendations import Recommendation, RecommendationPriority
from modules.gymbrain.providers.data_provider import DataProvider
from modules.gymbrain.rules.base import BaseRule, RuleResult


class RuleEngine:
    """Evaluates all registered rules and returns sorted recommendations.

    The rule engine is the central evaluation loop.
    Rules are evaluated in priority order, and results are merged,
    deduplicated, and sorted by confidence × priority.
    """

    def __init__(self) -> None:
        self._rules: list[BaseRule] = []
        self._rule_map: dict[str, BaseRule] = {}

    def register(self, rule: BaseRule) -> None:
        if rule.name in self._rule_map:
            msg = f"Rule '{rule.name}' is already registered"
            raise ValueError(msg)
        self._rules.append(rule)
        self._rule_map[rule.name] = rule
        self._rules.sort(key=lambda r: r.priority, reverse=True)

    def unregister(self, rule_name: str) -> None:
        if rule_name in self._rule_map:
            rule = self._rule_map.pop(rule_name)
            self._rules.remove(rule)

    def get_rules(self) -> list[BaseRule]:
        return list(self._rules)

    def evaluate(
        self,
        provider: DataProvider,
        context: dict[str, Any] | None = None,
        max_recommendations: int = 20,
    ) -> list[Recommendation]:
        results: list[Recommendation] = []
        seen_titles: set[str] = set()

        for rule in self._rules:
            result = rule.evaluate(provider, context)
            if result.triggered and result.recommendation:
                rec = result.recommendation
                rec.rule_name = rule.name

                if not rec.evidence:
                    rec.evidence = result.evidence
                if not rec.reason:
                    rec.reason = result.reason
                if not rec.confidence:
                    rec.confidence = result.confidence

                key = (rec.category.value, rec.title.lower())
                if key not in seen_titles:
                    seen_titles.add(key)
                    results.append(rec)

        results.sort(
            key=lambda r: (r.priority * r.confidence, r.priority),
            reverse=True,
        )

        return results[:max_recommendations]
