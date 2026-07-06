"""Adaptation Simulation Engine — evaluates adaptations through simulation before approval."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from shared.adaptive_programming.domain import (
    AdaptationScenario,
    AdaptiveConfig,
    AdaptiveContext,
    AdaptiveRecommendation,
    AdaptiveStrategy,
)


def _generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


class AdaptationSimulationEngine:
    """Evaluates candidate adaptations through simulation before approval."""

    def simulate_adaptation(
        self,
        rec: AdaptiveRecommendation,
        context: AdaptiveContext,
        config: AdaptiveConfig,
    ) -> AdaptationScenario:
        proposed = rec.suggested_value
        current = rec.current_value

        risk_factors = self._identify_risk_factors(rec, context, config)
        risk_penalty = min(len(risk_factors) * 0.15, 0.9)
        score = max(0.0, min(1.0, rec.expected_improvement * (1.0 - risk_penalty)))
        is_safe = risk_penalty < config.safety_threshold

        return AdaptationScenario(
            scenario_id=_generate_id("sc"),
            adaptation_type=rec.adaptation_type,
            proposed_value=proposed,
            current_value=current,
            context=context,
            score=score,
            is_safe=is_safe,
            risk_factors=risk_factors,
            simulated_at=datetime.now().isoformat(),
        )

    def _identify_risk_factors(
        self,
        rec: AdaptiveRecommendation,
        context: AdaptiveContext,
        config: AdaptiveConfig,
    ) -> list[str]:
        factors: list[str] = []
        if context.recovery_score < config.min_recovery_for_volume_increase:
            factors.append("recovery too low for increase")
        if context.fatigue_level > 0.8:
            factors.append("fatigue level critically high")
        if context.compliance_rate < config.min_compliance_for_adaptation:
            factors.append("compliance too low for adaptation")
        if rec.confidence < 0.5:
            factors.append("low recommendation confidence")
        change_ratio = abs(rec.suggested_value - rec.current_value) / max(abs(rec.current_value), 1)
        if change_ratio > config.max_volume_change_per_week:
            factors.append("change magnitude exceeds safe threshold")
        if context.knowledge_confidence < 0.3:
            factors.append("insufficient knowledge confidence")
        return factors

    def score_strategy(self, strategy: AdaptiveStrategy, context: AdaptiveContext) -> float:
        recovery_factor = context.recovery_score * 2.0
        fatigue_penalty = context.fatigue_level * 0.5
        multiplier = max(0.5, min(1.5, recovery_factor - fatigue_penalty))

        optimal_volume = strategy.base_volume * multiplier
        optimal_frequency = max(1, int(strategy.base_frequency * multiplier))

        volume_ratio = abs(strategy.current_volume - optimal_volume) / max(abs(strategy.current_volume), 1)
        volume_alignment = max(0.0, 1.0 - volume_ratio)

        freq_ratio = abs(strategy.current_frequency - optimal_frequency) / max(strategy.current_frequency, 1)
        freq_alignment = max(0.0, 1.0 - freq_ratio)

        return (volume_alignment + freq_alignment) / 2.0

    def reject_unsafe(
        self,
        scenarios: list[AdaptationScenario],
    ) -> tuple[list[AdaptationScenario], list[AdaptationScenario]]:
        safe = [s for s in scenarios if s.is_safe]
        unsafe = [s for s in scenarios if not s.is_safe]
        return safe, unsafe

    def simulate_all(
        self,
        recommendations: list[AdaptiveRecommendation],
        context: AdaptiveContext,
        config: AdaptiveConfig,
    ) -> list[AdaptationScenario]:
        return [self.simulate_adaptation(r, context, config) for r in recommendations]

    def compare_scenarios(
        self,
        scenarios: list[AdaptationScenario],
    ) -> list[AdaptationScenario]:
        return sorted(scenarios, key=lambda s: s.score, reverse=True)
