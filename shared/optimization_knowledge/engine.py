"""Optimization Knowledge Engine — Collects experiences, extracts patterns, derives rules, and generates insights."""

from __future__ import annotations

import uuid
from datetime import datetime

from shared.optimization_knowledge.domain import (
    InsightCategory,
    KnowledgeConfig,
    KnowledgeScope,
    OptimizationExperience,
    OptimizationInsight,
    OptimizationKnowledge,
    OptimizationOutcome,
    OptimizationPattern,
    OptimizationRecommendation,
    OptimizationRule,
    OutcomeClass,
    RuleEffect,
)
from shared.optimization_knowledge.patterns import PatternMiningEngine
from shared.optimization_knowledge.statistics import StatisticsEngine


def _generate_id(prefix: str = "kno") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class ExperienceEngine:
    """Collects and classifies optimization experiences."""

    def __init__(self, config: KnowledgeConfig | None = None) -> None:
        self.config = config or KnowledgeConfig()
        self._experiences: list[OptimizationExperience] = []

    def record_experience(
        self,
        plan_id: str,
        overall_score: float,
        avg_weekly_sets: int,
        sessions_per_week: int,
        total_weeks: int,
        total_sets: int,
        mesocycle_count: int,
        has_deload: bool,
        split_style: str | None = None,
        goal: str | None = None,
        success_threshold: float | None = None,
    ) -> OptimizationExperience:
        threshold = success_threshold if success_threshold is not None else self.config.success_threshold
        is_successful = overall_score >= threshold
        outcome = OptimizationOutcome(
            outcome_id=_generate_id("out"),
            experience_id="",
            outcome_class=OutcomeClass.SUCCESS if is_successful else OutcomeClass.FAILURE,
            score=overall_score,
            duration_weeks=total_weeks,
            created_at=datetime.now().isoformat(),
        )
        experience = OptimizationExperience(
            experience_id=_generate_id("exp"),
            plan_id=plan_id,
            overall_score=overall_score,
            avg_weekly_sets=avg_weekly_sets,
            sessions_per_week=sessions_per_week,
            total_weeks=total_weeks,
            total_sets=total_sets,
            mesocycle_count=mesocycle_count,
            has_deload=has_deload,
            split_style=split_style,
            goal=goal,
            is_successful=is_successful,
            outcome=outcome,
            created_at=datetime.now().isoformat(),
        )
        self._experiences.append(experience)
        return experience

    def classify_outcome(self, experience_id: str) -> OutcomeClass | None:
        for e in self._experiences:
            if e.experience_id == experience_id:
                return e.outcome.outcome_class
        return None

    def get_experiences(self) -> list[OptimizationExperience]:
        return list(self._experiences)

    def get_successful_experiences(self) -> list[OptimizationExperience]:
        return [e for e in self._experiences if e.is_successful]

    def get_failed_experiences(self) -> list[OptimizationExperience]:
        return [e for e in self._experiences if not e.is_successful]

    def clear(self) -> None:
        self._experiences.clear()


class KnowledgeExtractor:
    """Extracts patterns, rules, insights, and recommendations from collected experiences."""

    def __init__(self, config: KnowledgeConfig | None = None) -> None:
        self.config = config or KnowledgeConfig()
        self._pattern_miner = PatternMiningEngine(self.config)
        self._statistics_engine = StatisticsEngine(self.config)

    def extract_knowledge(
        self,
        experiences: list[OptimizationExperience],
        scope: KnowledgeScope = KnowledgeScope.GLOBAL,
        version: str = "",
        parent_version: str = "",
    ) -> OptimizationKnowledge:
        patterns = self._pattern_miner.mine_all(experiences, scope)
        statistics = self._statistics_engine.compute_all(experiences, scope)
        profiles = self._statistics_engine.build_profiles(experiences, scope)
        rules = self.derive_rules(patterns)
        insights = self.generate_insights(patterns, statistics)
        recommendations = self.generate_recommendations(rules, profiles)

        return OptimizationKnowledge(
            knowledge_id=_generate_id("know"),
            version=version,
            parent_version=parent_version,
            experiences=list(experiences),
            patterns=patterns,
            statistics=statistics,
            profiles=profiles,
            rules=rules,
            insights=insights,
            recommendations=recommendations,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
        )

    def derive_rules(
        self,
        patterns: list[OptimizationPattern],
    ) -> list[OptimizationRule]:
        rules: list[OptimizationRule] = []
        for pattern in patterns:
            if pattern.sample_size < self.config.min_pattern_sample:
                continue
            if pattern.success_rate >= 0.7:
                effect = RuleEffect.INCREASE
            elif pattern.success_rate <= 0.3:
                effect = RuleEffect.DECREASE
            else:
                effect = RuleEffect.MAINTAIN
            rule = OptimizationRule(
                rule_id=_generate_id("rule"),
                pattern_type=pattern.pattern_type,
                effect=effect,
                condition=(
                    f"{pattern.pattern_type.value} in "
                    f"[{pattern.value_range_min}, {pattern.value_range_max}]"
                ),
                description=(
                    f"{effect.label} {pattern.pattern_type.label.lower()} "
                    f"when success rate is {pattern.success_rate:.0%}"
                ),
                confidence=pattern.confidence,
                sample_size=pattern.sample_size,
                created_at=datetime.now().isoformat(),
            )
            rules.append(rule)
        return rules

    def generate_insights(
        self,
        patterns: list[OptimizationPattern],
        statistics: list,
    ) -> list[OptimizationInsight]:
        insights: list[OptimizationInsight] = []
        for pattern in patterns:
            if not pattern.is_reliable:
                continue
            if pattern.success_rate >= 0.7:
                category = InsightCategory.VOLUME_OPTIMIZATION
            elif pattern.success_rate <= 0.3:
                category = InsightCategory.FATIGUE_MANAGEMENT
            else:
                category = InsightCategory.GENERAL_OBSERVATION
            insight = OptimizationInsight(
                insight_id=_generate_id("insight"),
                category=category,
                title=f"{pattern.pattern_type.label}: {pattern.success_rate:.0%} success rate",
                description=(
                    f"Plans with {pattern.label} "
                    f"have a {pattern.success_rate:.0%} success rate "
                    f"(n={pattern.sample_size}, confidence={pattern.confidence:.0%})."
                ),
                supporting_pattern_ids=[pattern.pattern_id],
                confidence=pattern.confidence,
                created_at=datetime.now().isoformat(),
            )
            insights.append(insight)
        return insights

    def generate_recommendations(
        self,
        rules: list[OptimizationRule],
        profiles: list,
    ) -> list[OptimizationRecommendation]:
        recommendations: list[OptimizationRecommendation] = []
        for rule in rules:
            if rule.effect in (RuleEffect.MAINTAIN, RuleEffect.DECREASE):
                continue
            rec = OptimizationRecommendation(
                recommendation_id=_generate_id("rec"),
                title=f"Optimize {rule.pattern_type.label}",
                description=f"Consider adjusting {rule.pattern_type.label.lower()} based on {rule.condition}",
                pattern_type=rule.pattern_type,
                suggested_value_min=0.0,
                suggested_value_max=0.0,
                expected_improvement=rule.confidence * 0.1,
                confidence=rule.confidence,
                supporting_pattern_ids=[],
                created_at=datetime.now().isoformat(),
            )
            recommendations.append(rec)
        return recommendations
