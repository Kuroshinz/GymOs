from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from shared.explainability.domain import CounterfactualAction

logger = logging.getLogger("explainability.counterfactual")


@dataclass
class Counterfactual:
    counterfactual_id: str
    action: CounterfactualAction
    label: str
    description: str = ""
    current_value: str = ""
    proposed_value: str = ""
    expected_outcome: str = ""
    risk: float = 0.0
    confidence: float = 0.0
    delta: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def is_safe(self) -> bool:
        return self.risk < 0.5

    @property
    def risk_label(self) -> str:
        if self.risk < 0.25:
            return "Low"
        if self.risk < 0.5:
            return "Moderate"
        if self.risk < 0.75:
            return "High"
        return "Critical"

    def to_dict(self) -> dict[str, Any]:
        return {
            "counterfactual_id": self.counterfactual_id,
            "action": self.action.value,
            "label": self.label,
            "description": self.description,
            "current_value": self.current_value,
            "proposed_value": self.proposed_value,
            "expected_outcome": self.expected_outcome,
            "risk": self.risk,
            "confidence": self.confidence,
            "is_safe": self.is_safe,
            "risk_label": self.risk_label,
            "delta": self.delta,
            "timestamp": self.timestamp,
        }


_VOLUME_ACTIONS = [
    CounterfactualAction.INCREASE_VOLUME,
    CounterfactualAction.MAINTAIN_VOLUME,
    CounterfactualAction.DECREASE_VOLUME,
]

_FREQUENCY_ACTIONS = [
    CounterfactualAction.INCREASE_FREQUENCY,
    CounterfactualAction.DECREASE_FREQUENCY,
    CounterfactualAction.MAINTAIN_VOLUME,
]

_ADJUSTMENT_ACTIONS = [
    CounterfactualAction.ADJUST_INTENSITY,
    CounterfactualAction.ADJUST_NUTRITION,
    CounterfactualAction.ADJUST_RECOVERY,
    CounterfactualAction.MODIFY_EXERCISE,
]


class CounterfactualEngine:
    def __init__(self) -> None:
        self._history: list[Counterfactual] = []

    def generate(
        self,
        action: CounterfactualAction,
        current_value: str = "",
        context: dict[str, Any] | None = None,
    ) -> Counterfactual:
        ctx = context or {}
        proposed = self._compute_proposed(action, current_value, ctx)
        outcome = self._compute_outcome(action, proposed, ctx)
        risk = self._compute_risk(action, proposed, ctx)
        confidence = self._compute_confidence(action, ctx)

        cf = Counterfactual(
            counterfactual_id=uuid.uuid4().hex[:12],
            action=action,
            label=action.label,
            description=self._build_description(action, current_value, proposed),
            current_value=current_value,
            proposed_value=proposed,
            expected_outcome=outcome,
            risk=risk,
            confidence=confidence,
            delta={"current": current_value, "proposed": proposed, "change": proposed},
        )
        self._history.append(cf)
        return cf

    def generate_all(
        self,
        current_value: str = "",
        context: dict[str, Any] | None = None,
    ) -> list[Counterfactual]:
        results: list[Counterfactual] = []
        for action in CounterfactualAction:
            results.append(self.generate(action, current_value, context))
        results.sort(key=lambda c: c.confidence, reverse=True)
        return results

    def generate_for_volume(self, current_volume: str = "", context: dict | None = None) -> list[Counterfactual]:
        return [self.generate(a, current_volume, context) for a in _VOLUME_ACTIONS]

    def generate_for_frequency(self, current_frequency: str = "", context: dict | None = None) -> list[Counterfactual]:
        return [self.generate(a, current_frequency, context) for a in _FREQUENCY_ACTIONS]

    def generate_for_adjustment(self, current_value: str = "", context: dict | None = None) -> list[Counterfactual]:
        return [self.generate(a, current_value, context) for a in _ADJUSTMENT_ACTIONS]

    def compare(self, counterfactuals: list[Counterfactual]) -> list[Counterfactual]:
        return sorted(counterfactuals, key=lambda c: c.confidence, reverse=True)

    def get_history(self) -> list[Counterfactual]:
        return list(self._history)

    def clear_history(self) -> None:
        self._history.clear()

    def _compute_proposed(self, action: CounterfactualAction, current: str, ctx: dict) -> str:
        if not current:
            return action.label
        base = self._parse_numeric(current)
        if base is None:
            return action.label

        if action in (CounterfactualAction.INCREASE_VOLUME, CounterfactualAction.INCREASE_FREQUENCY):
            return f"{base * 1.15:.1f}"
        if action in (CounterfactualAction.DECREASE_VOLUME, CounterfactualAction.DECREASE_FREQUENCY):
            return f"{base * 0.85:.1f}"
        if action == CounterfactualAction.ADJUST_INTENSITY:
            return f"{base * 1.05:.1f}"
        return action.label

    def _compute_outcome(self, action: CounterfactualAction, proposed: str, ctx: dict) -> str:
        outcomes = {
            CounterfactualAction.INCREASE_VOLUME: "Potential strength gain with increased fatigue risk",
            CounterfactualAction.MAINTAIN_VOLUME: "Continued steady progress, low risk",
            CounterfactualAction.DECREASE_VOLUME: "Reduced fatigue, improved recovery, slower progression",
            CounterfactualAction.INCREASE_FREQUENCY: "More practice opportunities, higher recovery demand",
            CounterfactualAction.DECREASE_FREQUENCY: "More recovery time, fewer sessions per week",
            CounterfactualAction.MODIFY_EXERCISE: "Different stimulus, potential weak point improvement",
            CounterfactualAction.ADJUST_NUTRITION: "Energy balance change affects performance and recovery",
            CounterfactualAction.ADJUST_RECOVERY: "Enhanced recovery protocols improve readiness",
            CounterfactualAction.ADJUST_INTENSITY: "Heavier loads may increase strength but raise injury risk",
            CounterfactualAction.ADJUST_GOAL: "Shifted focus changes prioritization across dimensions",
        }
        return outcomes.get(action, "Alternative approach with different trade-offs")

    def _compute_risk(self, action: CounterfactualAction, proposed: str, ctx: dict) -> float:
        risks = {
            CounterfactualAction.INCREASE_VOLUME: 0.6,
            CounterfactualAction.MAINTAIN_VOLUME: 0.1,
            CounterfactualAction.DECREASE_VOLUME: 0.15,
            CounterfactualAction.INCREASE_FREQUENCY: 0.5,
            CounterfactualAction.DECREASE_FREQUENCY: 0.1,
            CounterfactualAction.MODIFY_EXERCISE: 0.3,
            CounterfactualAction.ADJUST_NUTRITION: 0.25,
            CounterfactualAction.ADJUST_RECOVERY: 0.1,
            CounterfactualAction.ADJUST_INTENSITY: 0.55,
            CounterfactualAction.ADJUST_GOAL: 0.2,
        }
        return risks.get(action, 0.3)

    def _compute_confidence(self, action: CounterfactualAction, ctx: dict) -> float:
        confidences = {
            CounterfactualAction.INCREASE_VOLUME: 0.7,
            CounterfactualAction.MAINTAIN_VOLUME: 0.9,
            CounterfactualAction.DECREASE_VOLUME: 0.75,
            CounterfactualAction.INCREASE_FREQUENCY: 0.65,
            CounterfactualAction.DECREASE_FREQUENCY: 0.7,
            CounterfactualAction.MODIFY_EXERCISE: 0.6,
            CounterfactualAction.ADJUST_NUTRITION: 0.7,
            CounterfactualAction.ADJUST_RECOVERY: 0.75,
            CounterfactualAction.ADJUST_INTENSITY: 0.55,
            CounterfactualAction.ADJUST_GOAL: 0.8,
        }
        base = confidences.get(action, 0.5)
        if ctx.get("high_confidence"):
            base = min(1.0, base + 0.1)
        return base

    def _parse_numeric(self, value: str) -> float | None:
        try:
            cleaned = value.strip().split()[0]
            return float(cleaned)
        except (ValueError, IndexError):
            return None

    def _build_description(self, action: CounterfactualAction, current: str, proposed: str) -> str:
        if action == CounterfactualAction.INCREASE_VOLUME:
            return f"Increase training volume from {current or 'current'} to {proposed}"
        if action == CounterfactualAction.MAINTAIN_VOLUME:
            return f"Maintain current volume at {current or 'current level'}"
        if action == CounterfactualAction.DECREASE_VOLUME:
            return f"Decrease training volume from {current or 'current'} to {proposed}"
        if action == CounterfactualAction.INCREASE_FREQUENCY:
            return f"Increase training frequency to {proposed} sessions per week"
        if action == CounterfactualAction.DECREASE_FREQUENCY:
            return f"Decrease training frequency to {proposed} sessions per week"
        return action.label
