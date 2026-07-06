from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CommandCenterData:
    header: dict = field(default_factory=dict)
    mission: dict = field(default_factory=dict)
    planning: dict = field(default_factory=dict)
    prediction: dict = field(default_factory=dict)
    recovery: dict = field(default_factory=dict)
    knowledge: dict = field(default_factory=dict)
    adaptive: dict = field(default_factory=dict)
    analytics: dict = field(default_factory=dict)
    system: dict = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


@dataclass
class MissionData:
    title: str = ""
    description: str = ""
    type: str = ""
    priority: str = "medium"
    source: str = ""
    confidence: float = 0.0
    estimated_duration: int = 0
    exercises: list = field(default_factory=list)
    target_volume: float = 0.0
    primary_muscles: list = field(default_factory=list)
    recovery_score: float = 0.0
    readiness: str = "unknown"
    recommendation: str = ""


@dataclass
class AdaptiveTimelineItem:
    date: str = ""
    adaptation_type: str = ""
    previous_value: str = ""
    new_value: str = ""
    reason: str = ""
    status: str = ""
    score: float = 0.0


@dataclass
class DecisionTimelineItem:
    date: str = ""
    decision_type: str = ""
    outcome: str = ""
    confidence: float = 0.0
    impact: str = ""


@dataclass
class KnowledgeUpdateItem:
    knowledge_id: str = ""
    domain: str = ""
    statement: str = ""
    confidence_score: float = 0.0
    change: float = 0.0
    version: str = ""
    timestamp: str = ""


@dataclass
class PredictionSummaryData:
    predictions: list = field(default_factory=list)
    accuracy: float = 0.0
    trend: str = "stable"
    updated_at: str = ""


@dataclass
class IntentData:
    current_goal: str = ""
    target_date: str = ""
    progress_percent: float = 0.0
    weekly_rate: float = 0.0
    adherence: float = 0.0
    phase: str = ""


@dataclass
class OptimizationInsightData:
    insights: list = field(default_factory=list)
    total_patterns: int = 0
    reliable_patterns: int = 0
    avg_confidence: float = 0.0


@dataclass
class RecoveryOverviewData:
    score: float = 0.0
    level: str = ""
    trend: str = "stable"
    sleep_score: float = 0.0
    stress_score: float = 0.0
    fatigue_score: float = 0.0
    flags: list = field(default_factory=list)


@dataclass
class TrainingReadinessData:
    readiness: str = "unknown"
    score: float = 0.0
    limiting_factor: str = ""
    recommendations: list = field(default_factory=list)


@dataclass
class CurrentMesocycleData:
    name: str = ""
    goal: str = ""
    phase: str = ""
    week: int = 0
    total_weeks: int = 0
    focus: str = ""
    volume_progress: float = 0.0
    next_deload_in: int = 0


@dataclass
class WeeklyReviewData:
    week_number: int = 0
    total_volume: float = 0.0
    sessions_completed: int = 0
    total_sessions: int = 0
    adherence_rate: float = 0.0
    prs_set: int = 0
    recovery_avg: float = 0.0
    notes: list = field(default_factory=list)


@dataclass
class SystemHealthData:
    overall: float = 0.0
    architecture: float = 0.0
    test_coverage: float = 0.0
    documentation: float = 0.0
    platform: float = 0.0
    rating: str = ""
    sub_scores: list = field(default_factory=list)


@dataclass
class CapabilityProgressData:
    total: int = 0
    complete: int = 0
    in_progress: int = 0
    not_started: int = 0
    blocked: int = 0
    overall_health: float = 0.0
    capabilities: list = field(default_factory=list)


@dataclass
class ReleaseReadinessData:
    version: str = ""
    milestone: str = ""
    blocking_issues: int = 0
    unmet_milestones: int = 0
    readiness_score: float = 0.0
    gaps: list = field(default_factory=list)


@dataclass
class KernelRuntimeData:
    status: str = ""
    uptime: str = ""
    active_plugins: int = 0
    total_plugins: int = 0
    memory_usage: str = ""
    event_queue_size: int = 0
    last_event: str = ""


@dataclass
class ProductStateData:
    version: str = ""
    capabilities_active: int = 0
    total_capabilities: int = 0
    release_phase: str = ""
    current_rfc: str = ""
    total_tests: int = 0
    passing_tests: int = 0
    coverage_pct: float = 0.0


@dataclass
class KnowledgeGraphData:
    nodes: list = field(default_factory=list)
    edges: list = field(default_factory=list)
    total_relationships: int = 0
    last_synced: str = ""
