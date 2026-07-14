"""Optimization Knowledge Metrics — Computes metrics for knowledge quality, coverage, and reliability."""

from __future__ import annotations

from datetime import datetime

from shared.optimization_knowledge.domain import (
    KnowledgeConfig,
    KnowledgeState,
    OptimizationKnowledge,
    OptimizationPattern,
    PatternType,
)


def _generate_id(prefix: str = "km") -> str:
    import uuid
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class KnowledgeMetrics:
    """Computes knowledge quality, coverage, and reliability metrics."""

    def __init__(self, config: KnowledgeConfig | None = None) -> None:
        self.config = config or KnowledgeConfig()

    def compute_metrics(
        self,
        knowledge: OptimizationKnowledge,
    ) -> KnowledgeMetricsResult:
        total = len(knowledge.patterns)
        reliable = sum(1 for p in knowledge.patterns if self._is_reliable(p))
        high_conf = sum(1 for p in knowledge.patterns if p.confidence >= 0.8)
        low_sample = sum(1 for p in knowledge.patterns if p.sample_size < 5)

        pattern_type_coverage = len(set(p.pattern_type for p in knowledge.patterns))
        all_types = len(PatternType)
        coverage_ratio = pattern_type_coverage / all_types

        total_experiences = len(knowledge.experiences)
        total_patterns_contributing = sum(p.sample_size for p in knowledge.patterns)
        avg_redundancy = (
            total_patterns_contributing / max(total_experiences, 1)
        )

        avg_confidence = (
            sum(p.confidence for p in knowledge.patterns) / max(total, 1)
        )
        avg_success_rate = (
            sum(p.success_rate for p in knowledge.patterns) / max(total, 1)
        )

        return KnowledgeMetricsResult(
            metrics_id=_generate_id(),
            total_patterns=total,
            reliable_patterns=reliable,
            high_confidence_patterns=high_conf,
            low_sample_patterns=low_sample,
            pattern_type_coverage=pattern_type_coverage,
            coverage_ratio=round(coverage_ratio, 4),
            avg_confidence=round(avg_confidence, 4),
            avg_success_rate=round(avg_success_rate, 4),
            avg_redundancy=round(avg_redundancy, 4),
            total_experiences=total_experiences,
            total_rules=len(knowledge.rules),
            total_insights=len(knowledge.insights),
            timestamp=datetime.now().isoformat(),
        )

    @staticmethod
    def _is_reliable(pattern: OptimizationPattern) -> bool:
        return pattern.sample_size >= 10 and pattern.confidence >= 0.8

    def compute_state_metrics(self, state: KnowledgeState) -> KnowledgeStateMetricsResult:
        exp_growth_needed = max(0, 100 - state.total_experiences)
        pattern_growth_needed = max(0, 50 - state.total_patterns)
        exp_per_version = (
            state.total_experiences / max(state.total_versions, 1)
        )
        return KnowledgeStateMetricsResult(
            metrics_id=_generate_id(),
            experience_growth_needed=exp_growth_needed,
            pattern_growth_needed=pattern_growth_needed,
            experiences_per_version=round(exp_per_version, 2),
            timestamp=datetime.now().isoformat(),
        )


class KnowledgeMetricsResult:
    """Result of knowledge quality metrics computation."""

    def __init__(
        self,
        metrics_id: str,
        total_patterns: int = 0,
        reliable_patterns: int = 0,
        high_confidence_patterns: int = 0,
        low_sample_patterns: int = 0,
        pattern_type_coverage: int = 0,
        coverage_ratio: float = 0.0,
        avg_confidence: float = 0.0,
        avg_success_rate: float = 0.0,
        avg_redundancy: float = 0.0,
        total_experiences: int = 0,
        total_rules: int = 0,
        total_insights: int = 0,
        timestamp: str = "",
    ) -> None:
        self.metrics_id = metrics_id
        self.total_patterns = total_patterns
        self.reliable_patterns = reliable_patterns
        self.high_confidence_patterns = high_confidence_patterns
        self.low_sample_patterns = low_sample_patterns
        self.pattern_type_coverage = pattern_type_coverage
        self.coverage_ratio = coverage_ratio
        self.avg_confidence = avg_confidence
        self.avg_success_rate = avg_success_rate
        self.avg_redundancy = avg_redundancy
        self.total_experiences = total_experiences
        self.total_rules = total_rules
        self.total_insights = total_insights
        self.timestamp = timestamp


class KnowledgeStateMetricsResult:
    """Result of state-based metrics computation."""

    def __init__(
        self,
        metrics_id: str,
        experience_growth_needed: int = 0,
        pattern_growth_needed: int = 0,
        experiences_per_version: float = 0.0,
        timestamp: str = "",
    ) -> None:
        self.metrics_id = metrics_id
        self.experience_growth_needed = experience_growth_needed
        self.pattern_growth_needed = pattern_growth_needed
        self.experiences_per_version = experiences_per_version
        self.timestamp = timestamp
