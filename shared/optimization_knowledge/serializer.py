"""Optimization Knowledge Serializer — Full dict/JSON round-trip serialization for all domain models."""

from __future__ import annotations

from typing import Any

from shared.optimization_knowledge.domain import (
    InsightCategory,
    KnowledgeScope,
    KnowledgeState,
    OptimizationExperience,
    OptimizationInsight,
    OptimizationKnowledge,
    OptimizationOutcome,
    OptimizationPattern,
    OptimizationProfile,
    OptimizationRecommendation,
    OptimizationRule,
    OptimizationStatistics,
    OutcomeClass,
    PatternType,
    RuleEffect,
)


class OptimizationKnowledgeSerializer:
    """Serializes and deserializes all optimization knowledge domain models."""

    @staticmethod
    def serialize_experience(exp: OptimizationExperience) -> dict[str, Any]:
        return {
            "experience_id": exp.experience_id,
            "plan_id": exp.plan_id,
            "overall_score": exp.overall_score,
            "avg_weekly_sets": exp.avg_weekly_sets,
            "sessions_per_week": exp.sessions_per_week,
            "total_weeks": exp.total_weeks,
            "total_sets": exp.total_sets,
            "mesocycle_count": exp.mesocycle_count,
            "has_deload": exp.has_deload,
            "split_style": exp.split_style,
            "goal": exp.goal,
            "is_successful": exp.is_successful,
            "outcome": OptimizationKnowledgeSerializer.serialize_outcome(exp.outcome),
            "created_at": exp.created_at,
        }

    @staticmethod
    def deserialize_experience(data: dict[str, Any]) -> OptimizationExperience:
        return OptimizationExperience(
            experience_id=data["experience_id"],
            plan_id=data["plan_id"],
            overall_score=data["overall_score"],
            avg_weekly_sets=data["avg_weekly_sets"],
            sessions_per_week=data["sessions_per_week"],
            total_weeks=data["total_weeks"],
            total_sets=data["total_sets"],
            mesocycle_count=data["mesocycle_count"],
            has_deload=data["has_deload"],
            split_style=data.get("split_style"),
            goal=data.get("goal"),
            is_successful=data["is_successful"],
            outcome=OptimizationKnowledgeSerializer.deserialize_outcome(data["outcome"]),
            created_at=data.get("created_at", ""),
        )

    @staticmethod
    def serialize_outcome(outcome: OptimizationOutcome) -> dict[str, Any]:
        return {
            "outcome_id": outcome.outcome_id,
            "experience_id": outcome.experience_id,
            "outcome_class": outcome.outcome_class.value,
            "score": outcome.score,
            "duration_weeks": outcome.duration_weeks,
            "created_at": outcome.created_at,
        }

    @staticmethod
    def deserialize_outcome(data: dict[str, Any]) -> OptimizationOutcome:
        return OptimizationOutcome(
            outcome_id=data["outcome_id"],
            experience_id=data["experience_id"],
            outcome_class=OutcomeClass(data["outcome_class"]),
            score=data["score"],
            duration_weeks=data["duration_weeks"],
            created_at=data.get("created_at", ""),
        )

    @staticmethod
    def serialize_pattern(pattern: OptimizationPattern) -> dict[str, Any]:
        return {
            "pattern_id": pattern.pattern_id,
            "pattern_type": pattern.pattern_type.value,
            "label": pattern.label,
            "description": pattern.description,
            "value_range_min": pattern.value_range_min,
            "value_range_max": pattern.value_range_max,
            "value_range_mean": pattern.value_range_mean,
            "success_rate": pattern.success_rate,
            "sample_size": pattern.sample_size,
            "confidence": pattern.confidence,
            "scope": pattern.scope.value,
            "tags": pattern.tags,
            "created_at": pattern.created_at,
        }

    @staticmethod
    def deserialize_pattern(data: dict[str, Any]) -> OptimizationPattern:
        return OptimizationPattern(
            pattern_id=data["pattern_id"],
            pattern_type=PatternType(data["pattern_type"]),
            label=data["label"],
            description=data.get("description", ""),
            value_range_min=data["value_range_min"],
            value_range_max=data["value_range_max"],
            value_range_mean=data.get("value_range_mean", 0.0),
            success_rate=data["success_rate"],
            sample_size=data["sample_size"],
            confidence=data["confidence"],
            scope=KnowledgeScope(data.get("scope", "global")),
            tags=data.get("tags", []),
            created_at=data.get("created_at", ""),
        )

    @staticmethod
    def serialize_statistics(stats: OptimizationStatistics) -> dict[str, Any]:
        return {
            "statistics_id": stats.statistics_id,
            "scope": stats.scope.value,
            "total_experiences": stats.total_experiences,
            "total_successes": stats.total_successes,
            "total_failures": stats.total_failures,
            "success_rate": stats.success_rate,
            "mean_score": stats.mean_score,
            "median_score": stats.median_score,
            "std_dev_score": stats.std_dev_score,
            "variance_score": stats.variance_score,
            "min_score": stats.min_score,
            "max_score": stats.max_score,
            "confidence_interval_lower": stats.confidence_interval_lower,
            "confidence_interval_upper": stats.confidence_interval_upper,
            "trend_direction": stats.trend_direction,
            "trend_slope": stats.trend_slope,
            "moving_average": stats.moving_average,
            "last_updated": stats.last_updated,
        }

    @staticmethod
    def deserialize_statistics(data: dict[str, Any]) -> OptimizationStatistics:
        return OptimizationStatistics(
            statistics_id=data["statistics_id"],
            scope=KnowledgeScope(data.get("scope", "global")),
            total_experiences=data.get("total_experiences", 0),
            total_successes=data.get("total_successes", 0),
            total_failures=data.get("total_failures", 0),
            success_rate=data.get("success_rate", 0.0),
            mean_score=data.get("mean_score", 0.0),
            median_score=data.get("median_score", 0.0),
            std_dev_score=data.get("std_dev_score", 0.0),
            variance_score=data.get("variance_score", 0.0),
            min_score=data.get("min_score", 0.0),
            max_score=data.get("max_score", 0.0),
            confidence_interval_lower=data.get("confidence_interval_lower", 0.0),
            confidence_interval_upper=data.get("confidence_interval_upper", 0.0),
            trend_direction=data.get("trend_direction", "insufficient"),
            trend_slope=data.get("trend_slope", 0.0),
            moving_average=data.get("moving_average", 0.0),
            last_updated=data.get("last_updated", ""),
        )

    @staticmethod
    def serialize_profile(profile: OptimizationProfile) -> dict[str, Any]:
        return {
            "profile_id": profile.profile_id,
            "scope": profile.scope.value,
            "best_sessions_per_week": profile.best_sessions_per_week,
            "best_total_weeks": profile.best_total_weeks,
            "best_avg_weekly_sets": profile.best_avg_weekly_sets,
            "best_split_style": profile.best_split_style,
            "best_mesocycle_count": profile.best_mesocycle_count,
            "best_goal": profile.best_goal,
            "avg_success_rate": profile.avg_success_rate,
            "total_experiences_analyzed": profile.total_experiences_analyzed,
            "created_at": profile.created_at,
        }

    @staticmethod
    def deserialize_profile(data: dict[str, Any]) -> OptimizationProfile:
        return OptimizationProfile(
            profile_id=data["profile_id"],
            scope=KnowledgeScope(data.get("scope", "global")),
            best_sessions_per_week=data.get("best_sessions_per_week", 0),
            best_total_weeks=data.get("best_total_weeks", 0),
            best_avg_weekly_sets=data.get("best_avg_weekly_sets", 0.0),
            best_split_style=data.get("best_split_style", ""),
            best_mesocycle_count=data.get("best_mesocycle_count", 0),
            best_goal=data.get("best_goal", ""),
            avg_success_rate=data.get("avg_success_rate", 0.0),
            total_experiences_analyzed=data.get("total_experiences_analyzed", 0),
            created_at=data.get("created_at", ""),
        )

    @staticmethod
    def serialize_insight(insight: OptimizationInsight) -> dict[str, Any]:
        return {
            "insight_id": insight.insight_id,
            "category": insight.category.value,
            "title": insight.title,
            "description": insight.description,
            "supporting_pattern_ids": insight.supporting_pattern_ids,
            "confidence": insight.confidence,
            "created_at": insight.created_at,
        }

    @staticmethod
    def deserialize_insight(data: dict[str, Any]) -> OptimizationInsight:
        return OptimizationInsight(
            insight_id=data["insight_id"],
            category=InsightCategory(data["category"]),
            title=data["title"],
            description=data.get("description", ""),
            supporting_pattern_ids=data.get("supporting_pattern_ids", []),
            confidence=data["confidence"],
            created_at=data.get("created_at", ""),
        )

    @staticmethod
    def serialize_rule(rule: OptimizationRule) -> dict[str, Any]:
        return {
            "rule_id": rule.rule_id,
            "pattern_type": rule.pattern_type.value,
            "effect": rule.effect.value,
            "condition": rule.condition,
            "description": rule.description,
            "confidence": rule.confidence,
            "sample_size": rule.sample_size,
            "created_at": rule.created_at,
        }

    @staticmethod
    def deserialize_rule(data: dict[str, Any]) -> OptimizationRule:
        return OptimizationRule(
            rule_id=data["rule_id"],
            pattern_type=PatternType(data["pattern_type"]),
            effect=RuleEffect(data["effect"]),
            condition=data.get("condition", ""),
            description=data.get("description", ""),
            confidence=data["confidence"],
            sample_size=data["sample_size"],
            created_at=data.get("created_at", ""),
        )

    @staticmethod
    def serialize_recommendation(rec: OptimizationRecommendation) -> dict[str, Any]:
        return {
            "recommendation_id": rec.recommendation_id,
            "title": rec.title,
            "description": rec.description,
            "pattern_type": rec.pattern_type.value,
            "suggested_value_min": rec.suggested_value_min,
            "suggested_value_max": rec.suggested_value_max,
            "expected_improvement": rec.expected_improvement,
            "confidence": rec.confidence,
            "supporting_pattern_ids": rec.supporting_pattern_ids,
            "created_at": rec.created_at,
        }

    @staticmethod
    def deserialize_recommendation(data: dict[str, Any]) -> OptimizationRecommendation:
        return OptimizationRecommendation(
            recommendation_id=data["recommendation_id"],
            title=data["title"],
            description=data.get("description", ""),
            pattern_type=PatternType(data["pattern_type"]),
            suggested_value_min=data["suggested_value_min"],
            suggested_value_max=data["suggested_value_max"],
            expected_improvement=data["expected_improvement"],
            confidence=data["confidence"],
            supporting_pattern_ids=data.get("supporting_pattern_ids", []),
            created_at=data.get("created_at", ""),
        )

    @staticmethod
    def serialize_knowledge(knowledge: OptimizationKnowledge) -> dict[str, Any]:
        return {
            "knowledge_id": knowledge.knowledge_id,
            "version": knowledge.version,
            "parent_version": knowledge.parent_version,
            "experiences": [
                OptimizationKnowledgeSerializer.serialize_experience(e)
                for e in knowledge.experiences
            ],
            "patterns": [
                OptimizationKnowledgeSerializer.serialize_pattern(p)
                for p in knowledge.patterns
            ],
            "statistics": [
                OptimizationKnowledgeSerializer.serialize_statistics(s)
                for s in knowledge.statistics
            ],
            "profiles": [
                OptimizationKnowledgeSerializer.serialize_profile(p)
                for p in knowledge.profiles
            ],
            "insights": [
                OptimizationKnowledgeSerializer.serialize_insight(i)
                for i in knowledge.insights
            ],
            "rules": [
                OptimizationKnowledgeSerializer.serialize_rule(r)
                for r in knowledge.rules
            ],
            "recommendations": [
                OptimizationKnowledgeSerializer.serialize_recommendation(r)
                for r in knowledge.recommendations
            ],
            "created_at": knowledge.created_at,
            "updated_at": knowledge.updated_at,
        }

    @staticmethod
    def deserialize_knowledge(data: dict[str, Any]) -> OptimizationKnowledge:
        return OptimizationKnowledge(
            knowledge_id=data["knowledge_id"],
            version=data["version"],
            parent_version=data.get("parent_version", ""),
            experiences=[
                OptimizationKnowledgeSerializer.deserialize_experience(e)
                for e in data.get("experiences", [])
            ],
            patterns=[
                OptimizationKnowledgeSerializer.deserialize_pattern(p)
                for p in data.get("patterns", [])
            ],
            statistics=[
                OptimizationKnowledgeSerializer.deserialize_statistics(s)
                for s in data.get("statistics", [])
            ],
            profiles=[
                OptimizationKnowledgeSerializer.deserialize_profile(p)
                for p in data.get("profiles", [])
            ],
            insights=[
                OptimizationKnowledgeSerializer.deserialize_insight(i)
                for i in data.get("insights", [])
            ],
            rules=[
                OptimizationKnowledgeSerializer.deserialize_rule(r)
                for r in data.get("rules", [])
            ],
            recommendations=[
                OptimizationKnowledgeSerializer.deserialize_recommendation(r)
                for r in data.get("recommendations", [])
            ],
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )

    @staticmethod
    def serialize_state(state: KnowledgeState) -> dict[str, Any]:
        return {
            "current_version": state.current_version,
            "total_experiences": state.total_experiences,
            "total_patterns": state.total_patterns,
            "total_insights": state.total_insights,
            "total_rules": state.total_rules,
            "total_versions": state.total_versions,
            "global_success_rate": state.global_success_rate,
            "global_mean_score": state.global_mean_score,
        }

    @staticmethod
    def deserialize_state(data: dict[str, Any]) -> KnowledgeState:
        return KnowledgeState(
            current_version=data.get("current_version", ""),
            total_experiences=data.get("total_experiences", 0),
            total_patterns=data.get("total_patterns", 0),
            total_insights=data.get("total_insights", 0),
            total_rules=data.get("total_rules", 0),
            total_versions=data.get("total_versions", 0),
            global_success_rate=data.get("global_success_rate", 0.0),
            global_mean_score=data.get("global_mean_score", 0.0),
        )
