"""Optimization Knowledge Domain — Experience, pattern, outcome, evidence, statistics, profile, knowledge, rule, insight, and recommendation models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

# ── Label Constants ─────────────────────────────────────────────────────

PATTERN_TYPE_LABELS: dict[str, str] = {
    "volume": "Volume",
    "frequency": "Frequency",
    "split": "Split",
    "recovery": "Recovery",
    "adherence": "Adherence",
    "deload": "Deload",
    "fatigue": "Fatigue",
}

OUTCOME_CLASS_LABELS: dict[str, str] = {
    "success": "Success",
    "failure": "Failure",
}

KNOWLEDGE_SCOPE_LABELS: dict[str, str] = {
    "global": "Global",
    "goal": "Goal",
    "split": "Split",
    "individual": "Individual",
}

INSIGHT_CATEGORY_LABELS: dict[str, str] = {
    "volume_optimization": "Volume Optimization",
    "frequency_optimization": "Frequency Optimization",
    "split_optimization": "Split Optimization",
    "recovery_optimization": "Recovery Optimization",
    "adherence_pattern": "Adherence Pattern",
    "deload_strategy": "Deload Strategy",
    "fatigue_management": "Fatigue Management",
    "general_observation": "General Observation",
}

RULE_EFFECT_LABELS: dict[str, str] = {
    "increase": "Increase",
    "decrease": "Decrease",
    "maintain": "Maintain",
}


# ── Enums ──────────────────────────────────────────────────────────────


class PatternType(Enum):
    VOLUME = "volume"
    FREQUENCY = "frequency"
    SPLIT = "split"
    RECOVERY = "recovery"
    ADHERENCE = "adherence"
    DELOAD = "deload"
    FATIGUE = "fatigue"

    @property
    def label(self) -> str:
        return PATTERN_TYPE_LABELS[self.value]


class OutcomeClass(Enum):
    SUCCESS = "success"
    FAILURE = "failure"

    @property
    def label(self) -> str:
        return OUTCOME_CLASS_LABELS[self.value]


class KnowledgeScope(Enum):
    GLOBAL = "global"
    GOAL = "goal"
    SPLIT = "split"
    INDIVIDUAL = "individual"

    @property
    def label(self) -> str:
        return KNOWLEDGE_SCOPE_LABELS[self.value]


class InsightCategory(Enum):
    VOLUME_OPTIMIZATION = "volume_optimization"
    FREQUENCY_OPTIMIZATION = "frequency_optimization"
    SPLIT_OPTIMIZATION = "split_optimization"
    RECOVERY_OPTIMIZATION = "recovery_optimization"
    ADHERENCE_PATTERN = "adherence_pattern"
    DELOAD_STRATEGY = "deload_strategy"
    FATIGUE_MANAGEMENT = "fatigue_management"
    GENERAL_OBSERVATION = "general_observation"

    @property
    def label(self) -> str:
        return INSIGHT_CATEGORY_LABELS[self.value]


class RuleEffect(Enum):
    INCREASE = "increase"
    DECREASE = "decrease"
    MAINTAIN = "maintain"

    @property
    def label(self) -> str:
        return RULE_EFFECT_LABELS[self.value]


# ── Core Domain Models ─────────────────────────────────────────────────


@dataclass(frozen=True)
class OptimizationOutcome:
    outcome_id: str = ""
    experience_id: str = ""
    outcome_class: OutcomeClass = OutcomeClass.FAILURE
    score: float = 0.0
    duration_weeks: int = 0
    created_at: str = ""


@dataclass(frozen=True)
class OptimizationExperience:
    experience_id: str = ""
    plan_id: str = ""
    overall_score: float = 0.0
    avg_weekly_sets: int = 0
    sessions_per_week: int = 0
    total_weeks: int = 0
    total_sets: int = 0
    mesocycle_count: int = 0
    has_deload: bool = False
    split_style: str | None = None
    goal: str | None = None
    is_successful: bool = False
    outcome: OptimizationOutcome = field(default_factory=lambda: OptimizationOutcome(
        outcome_id="", experience_id="", outcome_class=OutcomeClass.FAILURE,
        score=0.0, duration_weeks=0, created_at=datetime.now().isoformat(),
    ))
    created_at: str = ""


@dataclass(frozen=True)
class OptimizationPattern:
    pattern_id: str = ""
    pattern_type: PatternType = PatternType.VOLUME
    label: str = ""
    description: str = ""
    value_range_min: float = 0.0
    value_range_max: float = 0.0
    value_range_mean: float = 0.0
    success_rate: float = 0.0
    sample_size: int = 0
    confidence: float = 0.0
    scope: KnowledgeScope = KnowledgeScope.GLOBAL
    tags: list[str] = field(default_factory=list)
    created_at: str = ""

    @property
    def is_reliable(self) -> bool:
        return self.sample_size >= 10 and self.confidence >= 0.8


@dataclass(frozen=True)
class OptimizationEvidence:
    evidence_id: str = ""
    pattern_id: str = ""
    experience_id: str = ""
    supports: bool = True
    notes: str = ""


@dataclass(frozen=True)
class OptimizationStatistics:
    statistics_id: str = ""
    scope: KnowledgeScope = KnowledgeScope.GLOBAL
    total_experiences: int = 0
    total_successes: int = 0
    total_failures: int = 0
    success_rate: float = 0.0
    mean_score: float = 0.0
    median_score: float = 0.0
    std_dev_score: float = 0.0
    variance_score: float = 0.0
    min_score: float = 0.0
    max_score: float = 0.0
    confidence_interval_lower: float = 0.0
    confidence_interval_upper: float = 0.0
    trend_direction: str = "insufficient"
    trend_slope: float = 0.0
    moving_average: float = 0.0
    last_updated: str = ""

    def format_success_rate(self) -> str:
        return f"{self.success_rate * 100:.2f}%"


@dataclass(frozen=True)
class OptimizationProfile:
    profile_id: str = ""
    scope: KnowledgeScope = KnowledgeScope.GLOBAL
    best_sessions_per_week: int = 0
    best_total_weeks: int = 0
    best_avg_weekly_sets: float = 0.0
    best_split_style: str = ""
    best_mesocycle_count: int = 0
    best_goal: str = ""
    avg_success_rate: float = 0.0
    total_experiences_analyzed: int = 0
    created_at: str = ""


@dataclass(frozen=True)
class OptimizationInsight:
    insight_id: str = ""
    category: InsightCategory = InsightCategory.GENERAL_OBSERVATION
    title: str = ""
    description: str = ""
    supporting_pattern_ids: list[str] = field(default_factory=list)
    confidence: float = 0.0
    created_at: str = ""


@dataclass(frozen=True)
class OptimizationRule:
    rule_id: str = ""
    pattern_type: PatternType = PatternType.VOLUME
    effect: RuleEffect = RuleEffect.MAINTAIN
    condition: str = ""
    description: str = ""
    confidence: float = 0.0
    sample_size: int = 0
    created_at: str = ""


@dataclass(frozen=True)
class OptimizationRecommendation:
    recommendation_id: str = ""
    title: str = ""
    description: str = ""
    pattern_type: PatternType = PatternType.VOLUME
    suggested_value_min: float = 0.0
    suggested_value_max: float = 0.0
    expected_improvement: float = 0.0
    confidence: float = 0.0
    supporting_pattern_ids: list[str] = field(default_factory=list)
    created_at: str = ""


@dataclass(frozen=True)
class OptimizationKnowledge:
    knowledge_id: str = ""
    version: str = ""
    parent_version: str = ""
    experiences: list[OptimizationExperience] = field(default_factory=list)
    patterns: list[OptimizationPattern] = field(default_factory=list)
    statistics: list[OptimizationStatistics] = field(default_factory=list)
    profiles: list[OptimizationProfile] = field(default_factory=list)
    insights: list[OptimizationInsight] = field(default_factory=list)
    rules: list[OptimizationRule] = field(default_factory=list)
    recommendations: list[OptimizationRecommendation] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""


@dataclass(frozen=True)
class KnowledgeConfig:
    success_threshold: float = 0.7
    min_pattern_sample: int = 3
    confidence_z_score: float = 1.96
    enable_versioning: bool = True


@dataclass
class KnowledgeState:
    current_version: str = ""
    total_experiences: int = 0
    total_patterns: int = 0
    total_insights: int = 0
    total_rules: int = 0
    total_versions: int = 0
    global_success_rate: float = 0.0
    global_mean_score: float = 0.0
