from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from shared.explainability.domain import EvidenceSource
from shared.explainability.evidence import EvidenceItem
from shared.explainability.reason_tree import ReasonChain

logger = logging.getLogger("explainability.confidence")


@dataclass
class ConfidenceBreakdown:
    prediction: float = 0.0
    knowledge_quality: float = 0.0
    recovery_quality: float = 0.0
    planning_certainty: float = 0.0
    evidence_strength: float = 0.0

    @property
    def overall(self) -> float:
        weights = {"prediction": 0.25, "knowledge_quality": 0.2, "recovery_quality": 0.15, "planning_certainty": 0.15, "evidence_strength": 0.25}
        total = 0.0
        for key, weight in weights.items():
            total += getattr(self, key, 0.0) * weight
        return round(total, 4)

    @property
    def weakest(self) -> tuple[str, float]:
        items = [("prediction", self.prediction), ("knowledge_quality", self.knowledge_quality), ("recovery_quality", self.recovery_quality), ("planning_certainty", self.planning_certainty), ("evidence_strength", self.evidence_strength)]
        return min(items, key=lambda x: x[1])

    @property
    def strongest(self) -> tuple[str, float]:
        items = [("prediction", self.prediction), ("knowledge_quality", self.knowledge_quality), ("recovery_quality", self.recovery_quality), ("planning_certainty", self.planning_certainty), ("evidence_strength", self.evidence_strength)]
        return max(items, key=lambda x: x[1])

    def to_dict(self) -> dict[str, Any]:
        return {
            "prediction": self.prediction,
            "knowledge_quality": self.knowledge_quality,
            "recovery_quality": self.recovery_quality,
            "planning_certainty": self.planning_certainty,
            "evidence_strength": self.evidence_strength,
            "overall": self.overall,
            "weakest": {"component": self.weakest[0], "value": self.weakest[1]},
            "strongest": {"component": self.strongest[0], "value": self.strongest[1]},
        }


@dataclass
class ConfidenceResult:
    overall: float = 0.0
    breakdown: ConfidenceBreakdown | None = None
    evidence_count: int = 0
    source_count: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall": self.overall,
            "breakdown": self.breakdown.to_dict() if self.breakdown else None,
            "evidence_count": self.evidence_count,
            "source_count": self.source_count,
            "timestamp": self.timestamp,
        }


class ConfidenceEngine:
    def __init__(self) -> None:
        self._results: list[ConfidenceResult] = []

    def aggregate(self, evidence_items: list[EvidenceItem]) -> ConfidenceResult:
        if not evidence_items:
            result = ConfidenceResult(
                overall=0.0,
                breakdown=ConfidenceBreakdown(),
            )
            self._results.append(result)
            return result

        prediction_conf = self._avg_confidence(evidence_items, EvidenceSource.PREDICTION)
        knowledge_conf = self._avg_confidence(evidence_items, EvidenceSource.KNOWLEDGE)
        recovery_conf = self._avg_confidence(evidence_items, EvidenceSource.RECOVERY)
        planning_conf = self._avg_confidence(evidence_items, EvidenceSource.PLANNING)
        evidence_str = self._compute_evidence_strength(evidence_items)

        breakdown = ConfidenceBreakdown(
            prediction=prediction_conf,
            knowledge_quality=knowledge_conf,
            recovery_quality=recovery_conf,
            planning_certainty=planning_conf,
            evidence_strength=evidence_str,
        )
        sources = {i.source for i in evidence_items}
        result = ConfidenceResult(
            overall=breakdown.overall,
            breakdown=breakdown,
            evidence_count=len(evidence_items),
            source_count=len(sources),
        )
        self._results.append(result)
        return result

    def compute_from_chain(self, chain: ReasonChain) -> ConfidenceResult:
        if not chain.nodes:
            result = ConfidenceResult(overall=0.0, breakdown=ConfidenceBreakdown())
            self._results.append(result)
            return result
        node_confidences = [n.confidence for n in chain.nodes]
        evidence_items_count = sum(len(n.evidence_ids) for n in chain.nodes)

        breakdown = ConfidenceBreakdown(
            prediction=self._avg_confidence([], EvidenceSource.PREDICTION),
            knowledge_quality=self._avg_confidence([], EvidenceSource.KNOWLEDGE),
            recovery_quality=self._avg_confidence([], EvidenceSource.RECOVERY),
            planning_certainty=self._avg_confidence([], EvidenceSource.PLANNING),
            evidence_strength=min(1.0, evidence_items_count / 10),
        )

        if node_confidences:
            chain_conf = sum(node_confidences) / len(node_confidences)
            breakdown.prediction = max(breakdown.prediction, chain_conf)
            breakdown.evidence_strength = min(1.0, breakdown.evidence_strength + chain_conf * 0.3)

        result = ConfidenceResult(
            overall=breakdown.overall,
            breakdown=breakdown,
            evidence_count=evidence_items_count,
            source_count=len({n.node_type for n in chain.nodes}),
        )
        self._results.append(result)
        return result

    def _avg_confidence(self, items: list[EvidenceItem], source: EvidenceSource) -> float:
        filtered = [i for i in items if i.source == source]
        if not filtered:
            return 0.0
        return sum(i.confidence for i in filtered) / len(filtered)

    def _compute_evidence_strength(self, items: list[EvidenceItem]) -> float:
        if not items:
            return 0.0
        avg_conf = sum(i.confidence for i in items) / len(items)
        diversity = min(1.0, len({i.source for i in items}) / 4)
        return round(min(1.0, avg_conf * 0.6 + diversity * 0.4), 4)

    @property
    def results(self) -> list[ConfidenceResult]:
        return list(self._results)

    def clear_results(self) -> None:
        self._results.clear()
