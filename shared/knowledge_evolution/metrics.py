"""Knowledge Evolution Metrics — Compute evolution metrics from domain models."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from shared.knowledge_evolution.domain import (
    KnowledgeConflict,
    KnowledgeRecord,
    KnowledgeVersion,
    LifecycleStage,
)


@dataclass(frozen=True)
class EvolutionMetricsResult:
    """Result dataclass for all computed knowledge evolution metrics."""
    total_records: int = 0
    active_records: int = 0
    superseded_records: int = 0
    deprecated_records: int = 0
    archived_records: int = 0
    total_conflicts: int = 0
    resolved_conflicts: int = 0
    unresolved_conflicts: int = 0
    total_revisions: int = 0
    average_confidence: float = 0.0
    average_freshness: float = 0.0
    average_reliability: float = 0.0
    knowledge_stability: float = 0.0
    knowledge_volatility: float = 0.0
    knowledge_freshness: float = 0.0
    confidence_growth: float = 0.0
    revision_frequency: float = 0.0
    conflict_rate: float = 0.0


class KnowledgeEvolutionMetrics:
    """Computes evolution metrics from knowledge records, conflicts, and versions."""

    def compute_metrics(
        self,
        records: list[KnowledgeRecord],
        conflicts: list[KnowledgeConflict],
        versions: list[KnowledgeVersion],
    ) -> EvolutionMetricsResult:
        total_records = len(records)
        active_records = sum(1 for r in records if r.lifecycle_stage == LifecycleStage.ACTIVE)
        superseded_records = sum(1 for r in records if r.lifecycle_stage == LifecycleStage.SUPERSEDED)
        deprecated_records = sum(1 for r in records if r.lifecycle_stage == LifecycleStage.DEPRECATED)
        archived_records = sum(1 for r in records if r.lifecycle_stage == LifecycleStage.ARCHIVED)

        total_conflicts = len(conflicts)
        resolved_conflicts = sum(1 for c in conflicts if c.resolved)
        unresolved_conflicts = total_conflicts - resolved_conflicts

        total_revisions = len(versions)

        confidences = [r.confidence.score for r in records]
        freshnesses = [r.confidence.freshness_score for r in records]
        reliabilities = [r.confidence.reliability_score for r in records]

        average_confidence = mean(confidences) if confidences else 0.0
        average_freshness = mean(freshnesses) if freshnesses else 0.0
        average_reliability = mean(reliabilities) if reliabilities else 0.0

        divisor_records = max(total_records, 1)
        knowledge_stability = active_records / divisor_records
        knowledge_volatility = superseded_records / divisor_records
        knowledge_freshness = average_freshness
        confidence_growth = average_confidence
        revision_frequency = total_revisions / divisor_records
        conflict_rate = total_conflicts / divisor_records

        return EvolutionMetricsResult(
            total_records=total_records,
            active_records=active_records,
            superseded_records=superseded_records,
            deprecated_records=deprecated_records,
            archived_records=archived_records,
            total_conflicts=total_conflicts,
            resolved_conflicts=resolved_conflicts,
            unresolved_conflicts=unresolved_conflicts,
            total_revisions=total_revisions,
            average_confidence=average_confidence,
            average_freshness=average_freshness,
            average_reliability=average_reliability,
            knowledge_stability=knowledge_stability,
            knowledge_volatility=knowledge_volatility,
            knowledge_freshness=knowledge_freshness,
            confidence_growth=confidence_growth,
            revision_frequency=revision_frequency,
            conflict_rate=conflict_rate,
        )
