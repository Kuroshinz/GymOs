"""Bayesian-style confidence computation for knowledge evolution.

Agents use this engine to compute and update confidence scores for knowledge
records based on evidence accumulation, freshness decay, and source reliability.
"""
from __future__ import annotations

import math
from datetime import UTC, datetime

from shared.knowledge_evolution.domain import (
    ConfidenceLevel,
    EvolutionConfig,
    KnowledgeConfidence,
    KnowledgeEvidence,
)


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _latest_timestamp(evidence_list: list[KnowledgeEvidence]) -> str:
    valid = [e.timestamp for e in evidence_list if e.timestamp]
    return max(valid) if valid else ""


class ConfidenceEngine:
    """Computes and updates Bayesian-style confidence for knowledge records.

    Combines three dimensions into an overall confidence score:
      * Bayesian score — Beta-distribution posterior from support vs contradiction
      * Freshness score — exponential decay over time (configurable half-life)
      * Reliability score — source-type consistency of supporting evidence

    Overall = Bayesian × 0.4 + Freshness × 0.3 + Reliability × 0.3
    """

    def __init__(self, config: EvolutionConfig | None = None) -> None:
        self.config = config or EvolutionConfig()

    # ── Public API ──────────────────────────────────────────────────────

    def compute_confidence(
        self,
        knowledge_id: str,
        evidence_list: list[KnowledgeEvidence],
    ) -> KnowledgeConfidence:
        """Compute a fresh confidence from a list of evidence.

        Counts weighted support / contradiction, then evaluates all three
        sub-scores and combines them into the overall score.
        """
        support_count = sum(e.weight for e in evidence_list if e.supports)
        contradiction_count = sum(e.weight for e in evidence_list if not e.supports)
        total_evidence = len(evidence_list)

        if total_evidence == 0:
            return KnowledgeConfidence(
                confidence_id="",
                knowledge_id=knowledge_id,
                level=ConfidenceLevel.VERY_LOW,
                score=0.0,
                support_count=0,
                contradiction_count=0,
                total_evidence=0,
                freshness_score=0.0,
                reliability_score=0.5,
                last_updated=_now_iso(),
            )

        freshness_score = self._compute_freshness(
            _latest_timestamp(evidence_list),
        )
        reliability_score = self.compute_reliability_score(evidence_list)
        bayesian_score = self.compute_bayesian_score(
            int(support_count), int(contradiction_count),
        )

        overall = (
            bayesian_score * 0.4
            + freshness_score * 0.3
            + reliability_score * 0.3
        )
        level = self._score_to_level(overall)

        return KnowledgeConfidence(
            confidence_id="",
            knowledge_id=knowledge_id,
            level=level,
            score=_round4(overall),
            support_count=int(support_count),
            contradiction_count=int(contradiction_count),
            total_evidence=total_evidence,
            freshness_score=_round4(freshness_score),
            reliability_score=_round4(reliability_score),
            last_updated=_now_iso(),
        )

    def update_confidence(
        self,
        existing_confidence: KnowledgeConfidence,
        new_evidence: list[KnowledgeEvidence],
    ) -> KnowledgeConfidence:
        """Update an existing confidence with additional evidence.

        Accumulates support / contradiction counts and recomputes all
        sub-scores.  The freshness score is derived from the *newest*
        evidence timestamp (the latest among all evidence seen so far).
        """
        support_count = existing_confidence.support_count + sum(
            e.weight for e in new_evidence if e.supports
        )
        contradiction_count = existing_confidence.contradiction_count + sum(
            e.weight for e in new_evidence if not e.supports
        )
        total_evidence = existing_confidence.total_evidence + len(new_evidence)

        freshness_score = self._compute_freshness(
            _latest_timestamp(new_evidence),
        )
        reliability_score = self.compute_reliability_score(
            self._all_evidence_from_counts(
                int(support_count), int(contradiction_count),
            )
        )
        bayesian_score = self.compute_bayesian_score(
            int(support_count), int(contradiction_count),
        )

        overall = (
            bayesian_score * 0.4
            + freshness_score * 0.3
            + reliability_score * 0.3
        )
        level = self._score_to_level(overall)

        return KnowledgeConfidence(
            confidence_id=existing_confidence.confidence_id,
            knowledge_id=existing_confidence.knowledge_id,
            level=level,
            score=_round4(overall),
            support_count=int(support_count),
            contradiction_count=int(contradiction_count),
            total_evidence=total_evidence,
            freshness_score=_round4(freshness_score),
            reliability_score=_round4(reliability_score),
            last_updated=_now_iso(),
        )

    # ── Sub-scores ─────────────────────────────────────────────────

    def compute_freshness_score(self, timestamp: str) -> float:
        """Exponential decay freshness based on age vs. half-life.

        Formula:  exp(-age_days × ln(2) / half_life)

        A timestamp in the future yields 1.0 (perfect freshness).
        Missing or unparsable timestamps return 0.0.
        """
        if not timestamp:
            return 0.0
        try:
            dt = datetime.fromisoformat(timestamp)
        except (ValueError, TypeError):
            return 0.0
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        age = (datetime.now(UTC) - dt).total_seconds()
        age_days = age / 86400.0
        if age_days < 0:
            return 1.0
        half_life = self.config.freshness_half_life_days
        return math.exp(-age_days * math.log(2) / half_life)

    def compute_reliability_score(
        self,
        evidence_list: list[KnowledgeEvidence],
    ) -> float:
        """Source-consistency reliability score.

        When there are fewer than ``min_evidence_for_confidence`` items the
        score defaults to 0.5 (uncertain).  Otherwise it is the proportion of
        weighted support over total weighted evidence.
        """
        total_evidence = len(evidence_list)
        if total_evidence < self.config.min_evidence_for_confidence:
            return 0.5

        support = sum(e.weight for e in evidence_list if e.supports)
        contradiction = sum(e.weight for e in evidence_list if not e.supports)
        total = support + contradiction

        if total <= 0:
            return 0.5
        return support / total

    def compute_bayesian_score(
        self,
        support_count: int,
        contradiction_count: int,
        prior: float = 0.5,
    ) -> float:
        """Posterior mean of a Beta distribution with a uniform prior.

        ``alpha = support_count + 1``, ``beta = contradiction_count + 1``

        Formula:  (support + 1) / (support + contradiction + 2)

        The *prior* parameter is accepted for API symmetry; the uniform prior
        Beta(1, 1) is always used internally.
        """
        alpha = support_count + 1
        beta_ = contradiction_count + 1
        return alpha / (alpha + beta_)

    # ── Internal helpers ───────────────────────────────────────────

    def _compute_freshness(self, timestamp: str) -> float:
        """Thin wrapper that respects the config's freshness toggle."""
        if not self.config.enable_freshness_decay:
            return 1.0
        return self.compute_freshness_score(timestamp)

    @staticmethod
    def _score_to_level(score: float) -> ConfidenceLevel:
        if score >= 0.8:
            return ConfidenceLevel.VERY_HIGH
        if score >= 0.6:
            return ConfidenceLevel.HIGH
        if score >= 0.4:
            return ConfidenceLevel.MEDIUM
        if score >= 0.2:
            return ConfidenceLevel.LOW
        return ConfidenceLevel.VERY_LOW

    @staticmethod
    def _all_evidence_from_counts(
        support_count: int,
        contradiction_count: int,
    ) -> list[KnowledgeEvidence]:
        """Synthesize a minimum evidence list for reliability scoring.

        Used by *update_confidence* when the original ``KnowledgeEvidence``
        objects are no longer available — only the aggregated counts.
        """
        result: list[KnowledgeEvidence] = []
        for _ in range(support_count):
            result.append(
                KnowledgeEvidence(supports=True, weight=1.0)
            )
        for _ in range(contradiction_count):
            result.append(
                KnowledgeEvidence(supports=False, weight=1.0)
            )
        return result


def _round4(value: float) -> float:
    return round(value, 4)
