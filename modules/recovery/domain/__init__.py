"""GymOS Recovery Domain — first-class recovery entities for the Recovery Intelligence subsystem.

Every entity is strongly typed, deterministic, and directly modelable in SQLite.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto

# ─── Enums ──────────────────────────────────────────────────


class ReadinessLevel(Enum):
    """Training readiness level based on recovery assessment."""
    READY = "ready"
    GOOD = "good"
    CAUTION = "caution"
    FATIGUED = "fatigued"
    DELOAD = "deload"

    @property
    def score_threshold(self) -> float:
        return {
            ReadinessLevel.READY: 80.0,
            ReadinessLevel.GOOD: 60.0,
            ReadinessLevel.CAUTION: 40.0,
            ReadinessLevel.FATIGUED: 20.0,
            ReadinessLevel.DELOAD: 0.0,
        }[self]

    @property
    def label(self) -> str:
        labels = {
            ReadinessLevel.READY: "Ready to Train",
            ReadinessLevel.GOOD: "Good to Train",
            ReadinessLevel.CAUTION: "Train with Caution",
            ReadinessLevel.FATIGUED: "Significantly Fatigued",
            ReadinessLevel.DELOAD: "Deload Recommended",
        }
        return labels[self]

    @staticmethod
    def from_score(score: float) -> ReadinessLevel:
        if score >= 80:
            return ReadinessLevel.READY
        if score >= 60:
            return ReadinessLevel.GOOD
        if score >= 40:
            return ReadinessLevel.CAUTION
        if score >= 20:
            return ReadinessLevel.FATIGUED
        return ReadinessLevel.DELOAD


class FatigueLevel(Enum):
    """Subjective fatigue level reported by the user."""
    VERY_LOW = auto()
    LOW = auto()
    MODERATE = auto()
    HIGH = auto()
    VERY_HIGH = auto()


class SleepQuality(Enum):
    """Subjective sleep quality rating."""
    POOR = auto()
    FAIR = auto()
    GOOD = auto()
    VERY_GOOD = auto()
    EXCELLENT = auto()


class StressLevel(Enum):
    """Subjective stress level."""
    VERY_LOW = auto()
    LOW = auto()
    MODERATE = auto()
    HIGH = auto()
    VERY_HIGH = auto()


class SorenessLevel(Enum):
    """Muscle soreness rating."""
    NONE = auto()
    MILD = auto()
    MODERATE = auto()
    SEVERE = auto()
    VERY_SEVERE = auto()


class RecoveryTrend(Enum):
    """Direction of recovery over a lookback period."""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    VOLATILE = "volatile"


_RecoveryTrendDirection = RecoveryTrend  # Keep ref before dataclass shadow


class DeloadStatus(Enum):
    """Current deload status."""
    NONE = "none"
    DUE = "due"
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


# ─── Core Domain Models ─────────────────────────────────────


@dataclass
class RecoveryProfile:
    """User's recovery profile with baseline settings and preferences.

    Stored once per user, updated rarely.
    """
    id: str | None = None
    hrv_baseline: float = 65.0           # Baseline HRV (RMSSD)
    resting_hr_baseline: float = 60.0    # Baseline RHR (bpm)
    sleep_need_hours: float = 8.0        # Optimal sleep duration
    sleep_sensitivity: float = 1.0       # How much sleep affects recovery (1.0 = normal)
    stress_sensitivity: float = 1.0      # How much stress affects recovery (1.0 = normal)
    fatigue_sensitivity: float = 1.0     # How much fatigue affects recovery (1.0 = normal)
    deload_frequency_weeks: int = 6      # Deload every N weeks
    created_at: str = ""
    updated_at: str = ""


@dataclass
class RecoveryMetrics:
    """Computed recovery metrics for a single point in time."""
    recovery_score: float = 0.0           # 0-100 composite
    readiness_score: float = 0.0          # 0-100 readiness
    readiness_level: ReadinessLevel = ReadinessLevel.GOOD
    fatigue_score: float = 0.0            # 0-100 (higher = more fatigued)
    sleep_score: float = 0.0              # 0-100 sleep quality component
    stress_score: float = 0.0             # 0-100 stress component (higher = worse)
    muscle_recovery_score: float = 0.0    # 0-100 muscle recovery component
    training_fatigue_score: float = 0.0   # 0-100 training load component
    nutrition_adherence_score: float = 0.0  # 0-100 nutrition component
    bodyweight_trend_score: float = 0.0   # 0-100 bodyweight trend component
    consistency_score: float = 0.0        # 0-100 workout consistency component
    deload_benefit_score: float = 0.0     # 0-100 benefit from recent deload
    timestamp: str = ""
    explanation: str = ""


@dataclass
class RecoveryScore:
    """A single recovery score record with its component breakdown."""
    id: str | None = None
    date: str = ""
    overall_score: float = 0.0             # 0-100 composite
    readiness_score: float = 0.0           # 0-100
    readiness_level: ReadinessLevel = ReadinessLevel.GOOD
    fatigue_score: float = 0.0             # 0-100
    sleep_score: float = 0.0               # 0-100
    sleep_hours: float = 0.0               # Actual hours slept
    sleep_quality: SleepQuality | None = None
    stress_score: float = 0.0              # 0-100
    stress_level: StressLevel | None = None
    soreness_level: SorenessLevel | None = None
    muscle_recovery_score: float = 0.0     # 0-100
    training_fatigue_score: float = 0.0    # 0-100
    nutrition_adherence_score: float = 0.0  # 0-100
    bodyweight_trend_score: float = 0.0    # 0-100
    consistency_score: float = 0.0         # 0-100
    hrv_value: float | None = None      # Measured HRV
    resting_hr: float | None = None     # Measured RHR
    subjective_fatigue: int | None = None  # 1-5 scale
    note: str = ""
    created_at: str = ""

    @property
    def is_good(self) -> bool:
        return self.overall_score >= 60

    @property
    def is_critical(self) -> bool:
        return self.overall_score < 40

    @property
    def summary(self) -> str:
        level = ReadinessLevel.from_score(self.overall_score)
        return f"{level.label} (score: {self.overall_score:.0f}/100)"

    def to_metrics(self) -> RecoveryMetrics:
        return RecoveryMetrics(
            recovery_score=self.overall_score,
            readiness_score=self.readiness_score,
            readiness_level=self.readiness_level,
            fatigue_score=self.fatigue_score,
            sleep_score=self.sleep_score,
            stress_score=self.stress_score,
            muscle_recovery_score=self.muscle_recovery_score,
            training_fatigue_score=self.training_fatigue_score,
            nutrition_adherence_score=self.nutrition_adherence_score,
            bodyweight_trend_score=self.bodyweight_trend_score,
            consistency_score=self.consistency_score,
            timestamp=self.created_at or self.date,
        )


@dataclass
class RecoverySession:
    """A recovery session — user-reported recovery data for a given time.

    This is the primary input for recovery score calculation.
    """
    id: str | None = None
    date: str = ""
    sleep_hours: float = 0.0
    sleep_quality: SleepQuality | None = None
    stress_level: StressLevel | None = None
    fatigue_level: FatigueLevel | None = None
    soreness_level: SorenessLevel | None = None
    hrv_value: float | None = None
    resting_hr: float | None = None
    subjective_fatigue: int | None = None  # 1-5 scale
    note: str = ""
    created_at: str = ""


@dataclass
class SleepLog:
    """A sleep log entry."""
    id: str | None = None
    date: str = ""
    hours: float = 0.0
    quality: SleepQuality | None = None
    bedtime: str | None = None      # HH:MM format
    wake_time: str | None = None    # HH:MM format
    interruptions: int = 0
    note: str = ""
    created_at: str = ""


@dataclass
class StressLog:
    """A stress log entry."""
    id: str | None = None
    date: str = ""
    level: StressLevel = StressLevel.MODERATE
    source: str = ""                    # e.g., "work", "relationships", "health"
    note: str = ""
    created_at: str = ""


@dataclass
class ReadinessAssessment:
    """A readiness assessment combining recovery data into a training recommendation."""
    id: str | None = None
    date: str = ""
    readiness_score: float = 0.0
    readiness_level: ReadinessLevel = ReadinessLevel.GOOD
    recovery_score: float = 0.0
    fatigue_score: float = 0.0
    suggested_intensity_modifier: float = 1.0   # 0.0-1.0 scale for volume/intensity
    suggested_volume_modifier: float = 1.0      # 0.0-1.0 scale
    recommended_action: str = ""
    flags: list[str] = field(default_factory=list)
    created_at: str = ""


@dataclass
class RecoveryRecommendation:
    """A contextual recommendation based on recovery data."""
    id: str | None = None
    date: str = ""
    category: str = ""                 # "sleep", "stress", "training", "nutrition", "deload"
    priority: int = 0                  # 1-5 (5 = highest)
    message: str = ""
    reason: str = ""
    action: str = ""
    dismissed: bool = False
    created_at: str = ""


@dataclass
class RecoveryTrendAnalysis:
    """Recovery trend analysis over a lookback period."""
    direction: _RecoveryTrendDirection = _RecoveryTrendDirection.STABLE
    average_score: float = 0.0
    min_score: float = 0.0
    max_score: float = 0.0
    std_dev: float = 0.0
    slope: float = 0.0                   # Positive = improving
    days_analyzed: int = 0
    recent_scores: list[float] = field(default_factory=list)
    recent_dates: list[str] = field(default_factory=list)
    weekly_averages: list[float] = field(default_factory=list)
    explanation: str = ""


@dataclass
class FatigueFactors:
    """Fatigue factor breakdown with individual component scores."""
    training_volume_kg: float = 0.0
    training_intensity: float = 0.0      # Average RPE
    session_frequency: float = 0.0        # Sessions per week
    cumulative_volume_7d: float = 0.0     # Total volume last 7 days
    cumulative_volume_14d: float = 0.0    # Total volume last 14 days
    volume_ratio: float = 0.0             # 14d/7d ratio (>2 = accumulating)
    days_since_deload: int = 999
    recent_sleep_avg: float = 0.0
    recent_stress_avg: float = 0.0
    overall_fatigue: float = 0.0          # 0-100


@dataclass
class RecoveryFactors:
    """Recovery factor breakdown."""
    sleep_quality_score: float = 0.0
    sleep_duration_score: float = 0.0
    stress_level_score: float = 0.0
    hrv_score: float = 0.0
    nutrition_score: float = 0.0
    hydration_score: float = 0.0
    bodyweight_trend: float = 0.0
    training_consistency: float = 0.0
    muscle_recovery: float = 0.0
    deload_benefit: float = 0.0
    overall: float = 0.0


@dataclass
class DeloadPlan:
    """A deload plan with start/end dates and instructions."""
    id: str | None = None
    start_date: str = ""
    end_date: str = ""
    reason: str = ""
    volume_reduction_percent: float = 50.0   # 40-60%
    intensity_reduction_percent: float = 20.0
    instructions: str = ""
    status: DeloadStatus = DeloadStatus.PLANNED
    weeks_since_last_deload: int = 0
    created_at: str = ""

    @property
    def duration_days(self) -> int:
        try:
            start = datetime.strptime(self.start_date, "%Y-%m-%d")
            end = datetime.strptime(self.end_date, "%Y-%m-%d")
            return (end - start).days
        except (ValueError, TypeError):
            return 7

    @property
    def is_active(self) -> bool:
        today = datetime.now().strftime("%Y-%m-%d")
        return self.start_date <= today <= self.end_date if self.start_date and self.end_date else False


@dataclass
class RecoverySnapshot:
    """Complete recovery snapshot at a point in time — used for dashboard and reports."""
    date: str = ""
    recovery_score: float = 0.0
    readiness_score: float = 0.0
    readiness_level: ReadinessLevel = ReadinessLevel.GOOD
    fatigue_score: float = 0.0
    sleep_score: float = 0.0
    stress_score: float = 0.0
    muscle_recovery_score: float = 0.0
    trend: _RecoveryTrendDirection = _RecoveryTrendDirection.STABLE
    flags: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


@dataclass
class RecoveryHistory:
    """Historical recovery data for analysis and charting."""
    scores: list[RecoveryScore] = field(default_factory=list)
    sleep_logs: list[SleepLog] = field(default_factory=list)
    stress_logs: list[StressLog] = field(default_factory=list)
    readiness_assessments: list[ReadinessAssessment] = field(default_factory=list)

    @property
    def days_of_data(self) -> int:
        return len(self.scores)

    @property
    def average_score(self) -> float:
        if not self.scores:
            return 0.0
        return sum(s.overall_score for s in self.scores) / len(self.scores)

    @property
    def latest_score(self) -> RecoveryScore | None:
        return self.scores[-1] if self.scores else None
