"""Confidence Scoring — computes confidence scores for state assessments and release readiness.

Determines how confident we are in the current product state evaluation
and whether the product is ready for release.
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.capabilities import registry as _cap_registry
from shared.capabilities.enums import CapabilityStatus
from shared.kernel.kernel_context import assess_release_readiness
from shared.state.indicators import IndicatorSet


@dataclass(frozen=True)
class ConfidenceResult:
    """Confidence assessment for the current product state."""

    state_confidence: float = 0.0      # 0-100: confidence in state determination
    release_confidence: float = 0.0    # 0-100: confidence in release readiness
    data_quality: float = 0.0          # 0-100: quality of underlying data
    coverage_confidence: float = 0.0   # 0-100: how well capabilities are measured
    timestamp_confidence: float = 0.0  # 0-100: freshness of data
    overall: float = 0.0               # 0-100: weighted composite
    factors: tuple[str, ...] = ()


class ConfidenceScorer:
    """Computes confidence scores for product state and release assessments.

    Stateless — every call computes fresh from canonical sources.
    """

    def score(self, indicators: IndicatorSet | None = None) -> ConfidenceResult:
        """Compute confidence scores for the current product state."""
        caps = _cap_registry.list_all()

        # Data quality: how many capabilities have complete health data
        complete_health = sum(1 for c in caps if c.health.overall > 0)
        data_quality = (complete_health / max(len(caps), 1)) * 100.0

        # Coverage confidence: how well capabilities are measured
        measured = sum(1 for c in caps
                       if c.status in (CapabilityStatus.COMPLETE, CapabilityStatus.IN_PROGRESS))
        coverage_confidence = (measured / max(len(caps), 1)) * 100.0

        # State confidence: based on data quality and coverage
        state_confidence = round(data_quality * 0.5 + coverage_confidence * 0.5, 1)

        # Release confidence: based on release readiness assessment
        release = assess_release_readiness(_cap_registry, "0.5.0")
        release_confidence = round(release.score, 1)

        # Timestamp confidence: all capabilities should have a last_updated (simplified)
        timestamp_confidence = 100.0  # Data is current by construction

        # Overall: weighted composite
        overall = round(
            state_confidence * 0.30 +
            release_confidence * 0.30 +
            data_quality * 0.15 +
            coverage_confidence * 0.15 +
            timestamp_confidence * 0.10,
            1,
        )

        factors = self._build_factors(
            data_quality, coverage_confidence, state_confidence, release_confidence, timestamp_confidence
        )

        return ConfidenceResult(
            state_confidence=state_confidence,
            release_confidence=release_confidence,
            data_quality=round(data_quality, 1),
            coverage_confidence=round(coverage_confidence, 1),
            timestamp_confidence=timestamp_confidence,
            overall=overall,
            factors=tuple(factors),
        )

    def _build_factors(
        self, data_q: float, coverage: float, state_conf: float, release_conf: float, ts_conf: float
    ) -> list[str]:
        factors: list[str] = []
        if data_q >= 80:
            factors.append("High data quality across capabilities")
        elif data_q >= 50:
            factors.append("Moderate data quality, some gaps")
        else:
            factors.append("Low data quality, significant gaps")

        if coverage >= 80:
            factors.append("Good capability measurement coverage")
        elif coverage >= 50:
            factors.append("Partial capability coverage")
        else:
            factors.append("Poor capability coverage")

        if state_conf >= 70:
            factors.append("Confident in state determination")
        elif state_conf >= 40:
            factors.append("Moderate state confidence")
        else:
            factors.append("Low state confidence — more data needed")

        if release_conf >= 70:
            factors.append("High release confidence")
        elif release_conf >= 40:
            factors.append("Moderate release confidence")
        else:
            factors.append("Low release confidence")

        return factors
