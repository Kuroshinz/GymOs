"""Adaptive Programming Metrics — Compute adaptation metrics from domain models."""

from __future__ import annotations

from datetime import datetime

from shared.adaptive_programming.domain import (
    AdaptiveMetrics,
    AdaptivePlan,
    DecisionStatus,
)


class AdaptiveMetricsCalculator:
    """Computes adaptation quality metrics from an adaptive plan and decisions."""

    def compute_metrics(
        self,
        plan: AdaptivePlan,
        decisions: list,
    ) -> AdaptiveMetrics:
        total_adaptations = len(decisions)
        approved = sum(1 for d in decisions if d.status == DecisionStatus.APPROVED)
        rejected = sum(1 for d in decisions if d.status == DecisionStatus.REJECTED)
        rolled_back = sum(1 for d in decisions if d.status == DecisionStatus.ROLLED_BACK)
        completed = sum(1 for d in decisions if d.status == DecisionStatus.COMPLETED)
        completed_successfully = sum(
            1 for d in decisions
            if d.status == DecisionStatus.COMPLETED and d.score > 0
        )

        weeks = max(plan.strategy.weeks_into_phase, 1)
        adaptation_frequency = total_adaptations / weeks

        total = max(total_adaptations, 1)
        adaptation_quality = approved / total
        success_rate = completed_successfully / max(completed, 1)
        rollback_rate = rolled_back / max(approved + completed, 1)
        strategy_stability = 1 - (approved + rolled_back) / total

        return AdaptiveMetrics(
            total_adaptations=total_adaptations,
            approved_adaptations=approved,
            rejected_adaptations=rejected,
            rolled_back_adaptations=rolled_back,
            adaptation_frequency=adaptation_frequency,
            adaptation_quality=adaptation_quality,
            success_rate=success_rate,
            rollback_rate=rollback_rate,
            strategy_stability=strategy_stability,
            timestamp=datetime.now().isoformat(),
        )
