"""Optimization Knowledge Query Engine — Queries the best split, volume, frequency, mesocycle, and progression from accumulated knowledge."""

from __future__ import annotations

from shared.optimization_knowledge.domain import (
    KnowledgeScope,
    OptimizationKnowledge,
    OptimizationPattern,
    OptimizationProfile,
    OptimizationRecommendation,
    PatternType,
)


class KnowledgeQueryEngine:
    """Queries accumulated knowledge for optimal training parameters."""

    def __init__(self) -> None:
        pass

    def best_split(
        self,
        knowledge: OptimizationKnowledge,
        min_samples: int = 5,
    ) -> OptimizationPattern | None:
        splits = [p for p in knowledge.patterns if p.pattern_type == PatternType.SPLIT and p.sample_size >= min_samples]
        if not splits:
            return None
        return max(splits, key=lambda p: p.success_rate)

    def best_volume(
        self,
        knowledge: OptimizationKnowledge,
        min_samples: int = 5,
    ) -> OptimizationPattern | None:
        volumes = [p for p in knowledge.patterns if p.pattern_type == PatternType.VOLUME and p.sample_size >= min_samples]
        if not volumes:
            return None
        return max(volumes, key=lambda p: p.success_rate)

    def best_frequency(
        self,
        knowledge: OptimizationKnowledge,
        min_samples: int = 5,
    ) -> OptimizationPattern | None:
        freqs = [p for p in knowledge.patterns if p.pattern_type == PatternType.FREQUENCY and p.sample_size >= min_samples]
        if not freqs:
            return None
        return max(freqs, key=lambda p: p.success_rate)

    def best_mesocycle(
        self,
        knowledge: OptimizationKnowledge,
        min_samples: int = 5,
    ) -> OptimizationPattern | None:
        adhs = [p for p in knowledge.patterns if p.pattern_type == PatternType.ADHERENCE and p.sample_size >= min_samples]
        if not adhs:
            return None
        return max(adhs, key=lambda p: p.success_rate)

    def best_progression(
        self,
        knowledge: OptimizationKnowledge,
        min_samples: int = 5,
    ) -> OptimizationPattern | None:
        fats = [p for p in knowledge.patterns if p.pattern_type == PatternType.FATIGUE and p.sample_size >= min_samples]
        if not fats:
            return None
        return max(fats, key=lambda p: p.success_rate)

    def best_profile(
        self,
        knowledge: OptimizationKnowledge,
        goal: str | None = None,
    ) -> OptimizationProfile | None:
        if goal:
            for p in knowledge.profiles:
                if p.best_goal == goal:
                    return p
        if knowledge.profiles:
            best = max(knowledge.profiles, key=lambda p: p.avg_success_rate)
            return best
        return None

    def query_by_pattern_type(
        self,
        knowledge: OptimizationKnowledge,
        pattern_type: PatternType,
        min_samples: int = 5,
    ) -> list[OptimizationPattern]:
        return [
            p for p in knowledge.patterns
            if p.pattern_type == pattern_type and p.sample_size >= min_samples
        ]

    def query_by_scope(
        self,
        knowledge: OptimizationKnowledge,
        scope: KnowledgeScope,
    ) -> list[OptimizationPattern]:
        return [p for p in knowledge.patterns if p.scope == scope]

    def top_recommendations(
        self,
        recommendations: list[OptimizationRecommendation],
        min_confidence: float = 0.8,
        max_results: int = 5,
    ) -> list[OptimizationRecommendation]:
        confident = [r for r in recommendations if r.confidence >= min_confidence]
        confident.sort(key=lambda r: r.expected_improvement, reverse=True)
        return confident[:max_results]
