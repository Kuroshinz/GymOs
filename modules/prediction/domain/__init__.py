from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto


class PredictionType(Enum):
    NEXT_PR_PROBABILITY = "next_pr_probability"
    PLATEAU_PROBABILITY = "plateau_probability"
    RECOVERY_DECLINE = "recovery_decline"
    BODYWEIGHT_TREND = "bodyweight_trend"
    GOAL_ETA = "goal_eta"
    MRV_VIOLATION_RISK = "mrv_violation_risk"
    DELOAD_PROBABILITY = "deload_probability"
    CONSISTENCY_DECAY = "consistency_decay"
    WORKOUT_COMPLETION_PROBABILITY = "workout_completion_probability"

    @property
    def label(self) -> str:
        return {
            PredictionType.NEXT_PR_PROBABILITY: "Next PR Probability",
            PredictionType.PLATEAU_PROBABILITY: "Plateau Probability",
            PredictionType.RECOVERY_DECLINE: "Recovery Decline",
            PredictionType.BODYWEIGHT_TREND: "Bodyweight Trend",
            PredictionType.GOAL_ETA: "Goal ETA",
            PredictionType.MRV_VIOLATION_RISK: "MRV Violation Risk",
            PredictionType.DELOAD_PROBABILITY: "Deload Probability",
            PredictionType.CONSISTENCY_DECAY: "Consistency Decay",
            PredictionType.WORKOUT_COMPLETION_PROBABILITY: "Workout Completion Probability",
        }[self]


class PredictionWindow(Enum):
    NEXT_3_DAYS = "3d"
    NEXT_7_DAYS = "7d"
    NEXT_14_DAYS = "14d"
    NEXT_28_DAYS = "28d"

    @property
    def days(self) -> int:
        return {"3d": 3, "7d": 7, "14d": 14, "28d": 28}[self.value]

    @property
    def label(self) -> str:
        return {"3d": "Next 3 Days", "7d": "Next 7 Days", "14d": "Next 14 Days", "28d": "Next 28 Days"}[self.value]


class ConfidenceLevel(Enum):
    VERY_LOW = auto()
    LOW = auto()
    MODERATE = auto()
    HIGH = auto()
    VERY_HIGH = auto()

    @property
    def score(self) -> float:
        return {ConfidenceLevel.VERY_LOW: 0.1, ConfidenceLevel.LOW: 0.3, ConfidenceLevel.MODERATE: 0.5, ConfidenceLevel.HIGH: 0.7, ConfidenceLevel.VERY_HIGH: 0.9}[self]

    @property
    def label(self) -> str:
        return {ConfidenceLevel.VERY_LOW: "Very Low", ConfidenceLevel.LOW: "Low", ConfidenceLevel.MODERATE: "Moderate", ConfidenceLevel.HIGH: "High", ConfidenceLevel.VERY_HIGH: "Very High"}[self]

    @staticmethod
    def from_score(score: float) -> ConfidenceLevel:
        if score >= 0.8:
            return ConfidenceLevel.VERY_HIGH
        if score >= 0.6:
            return ConfidenceLevel.HIGH
        if score >= 0.4:
            return ConfidenceLevel.MODERATE
        if score >= 0.2:
            return ConfidenceLevel.LOW
        return ConfidenceLevel.VERY_LOW


class TrendModel(Enum):
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"
    POLYNOMIAL = "polynomial"
    MOVING_AVERAGE = "moving_average"
    HOLT_WINTERS = "holt_winters"

    @property
    def label(self) -> str:
        return {
            TrendModel.LINEAR: "Linear",
            TrendModel.EXPONENTIAL: "Exponential",
            TrendModel.LOGARITHMIC: "Logarithmic",
            TrendModel.POLYNOMIAL: "Polynomial",
            TrendModel.MOVING_AVERAGE: "Moving Average",
            TrendModel.HOLT_WINTERS: "Holt-Winters",
        }[self]


@dataclass
class PredictionConfidence:
    score: float = 0.0
    level: ConfidenceLevel = ConfidenceLevel.MODERATE
    factors: list[str] = field(default_factory=list)
    data_quality: float = 1.0
    sample_size: int = 0
    variance: float = 0.0

    def __post_init__(self) -> None:
        self.level = ConfidenceLevel.from_score(self.score)


@dataclass
class PredictionEvidence:
    source: str = ""
    data_point: str = ""
    value: float = 0.0
    timestamp: str = ""
    relevance: float = 1.0

    def __post_init__(self) -> None:
        self.relevance = max(0.0, min(self.relevance, 1.0))


@dataclass
class PredictionExplanation:
    summary: str = ""
    reasoning: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    risk_factors: list[str] = field(default_factory=list)
    evidence: list[PredictionEvidence] = field(default_factory=list)


@dataclass
class ForecastPoint:
    date: str = ""
    predicted_value: float = 0.0
    lower_bound: float = 0.0
    upper_bound: float = 0.0
    confidence_at_point: float = 0.0

    def __post_init__(self) -> None:
        self.lower_bound = min(self.lower_bound, self.predicted_value)
        self.upper_bound = max(self.upper_bound, self.predicted_value)
        self.confidence_at_point = max(0.0, min(self.confidence_at_point, 1.0))


@dataclass
class Forecast:
    prediction_type: PredictionType = PredictionType.NEXT_PR_PROBABILITY
    window: PredictionWindow = PredictionWindow.NEXT_7_DAYS
    points: list[ForecastPoint] = field(default_factory=list)
    trend_model: TrendModel = TrendModel.LINEAR
    confidence: PredictionConfidence = field(default_factory=PredictionConfidence)
    explanation: PredictionExplanation = field(default_factory=PredictionExplanation)
    created_at: str = ""

    @property
    def latest_point(self) -> ForecastPoint | None:
        return self.points[-1] if self.points else None

    @property
    def direction(self) -> str:
        if len(self.points) < 2:
            return "stable"
        first = self.points[0].predicted_value
        last = self.points[-1].predicted_value
        diff = last - first
        if abs(diff) < 0.01:
            return "stable"
        return "increasing" if diff > 0 else "decreasing"


@dataclass
class PredictionScenario:
    name: str = ""
    description: str = ""
    probability: float = 0.5
    conditions: list[str] = field(default_factory=list)
    impact: str = ""
    confidence: PredictionConfidence = field(default_factory=PredictionConfidence)


@dataclass
class Prediction:
    id: str | None = None
    prediction_type: PredictionType = PredictionType.NEXT_PR_PROBABILITY
    window: PredictionWindow = PredictionWindow.NEXT_7_DAYS
    value: float = 0.0
    probability: float = 0.0
    confidence: PredictionConfidence = field(default_factory=PredictionConfidence)
    explanation: PredictionExplanation = field(default_factory=PredictionExplanation)
    forecast: Forecast | None = None
    scenarios: list[PredictionScenario] = field(default_factory=list)
    created_at: str = ""
    expires_at: str = ""
    is_active: bool = True

    @property
    def is_expired(self) -> bool:
        if not self.expires_at:
            return False
        try:
            exp = datetime.strptime(self.expires_at, "%Y-%m-%d")
            return exp < datetime.now()
        except (ValueError, TypeError):
            return False


@dataclass
class FactorContribution:
    factor_name: str = ""
    contribution: float = 0.0
    direction: str = "positive"
    description: str = ""
    weight: float = 0.0

    def __post_init__(self) -> None:
        self.direction = "positive" if self.contribution >= 0 else "negative"
        self.weight = max(0.0, min(self.weight, 1.0))


@dataclass
class ReasonStep:
    step_number: int = 0
    premise: str = ""
    conclusion: str = ""
    confidence_at_step: float = 0.0


@dataclass
class ReasonChain:
    steps: list[ReasonStep] = field(default_factory=list)
    final_conclusion: str = ""
    overall_confidence: float = 0.0

    @property
    def length(self) -> int:
        return len(self.steps)


@dataclass
class NLExplanation:
    short: str = ""
    detailed: str = ""
    actionable: str = ""
    language: str = "en"


@dataclass
class MRExplanation:
    top_factors: list[dict] = field(default_factory=list)
    confidence_breakdown: dict = field(default_factory=dict)
    evidence_summary: list[dict] = field(default_factory=list)
    assumptions_used: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    model_version: str = "1.0"


@dataclass
class ExplainabilityDetail:
    factor_contributions: list[FactorContribution] = field(default_factory=list)
    reason_chain: ReasonChain = field(default_factory=ReasonChain)
    nl_explanation: NLExplanation = field(default_factory=NLExplanation)
    mr_explanation: MRExplanation = field(default_factory=MRExplanation)
    evidence_ranking: list[PredictionEvidence] = field(default_factory=list)


# ─── Scenario Engine Entities ─────────────────────────────


class ScenarioIntervention(Enum):
    INCREASE_VOLUME = "increase_volume"
    DECREASE_VOLUME = "decrease_volume"
    EARLY_DELOAD = "early_deload"
    LATE_DELOAD = "late_deload"
    INCREASE_CALORIES = "increase_calories"
    DECREASE_CALORIES = "decrease_calories"
    HIGHER_SLEEP = "higher_sleep"
    LOWER_SLEEP = "lower_sleep"
    HIGHER_ADHERENCE = "higher_adherence"
    LOWER_ADHERENCE = "lower_adherence"

    @property
    def label(self) -> str:
        return {
            ScenarioIntervention.INCREASE_VOLUME: "Increase Volume",
            ScenarioIntervention.DECREASE_VOLUME: "Decrease Volume",
            ScenarioIntervention.EARLY_DELOAD: "Early Deload",
            ScenarioIntervention.LATE_DELOAD: "Late Deload",
            ScenarioIntervention.INCREASE_CALORIES: "Increase Calories",
            ScenarioIntervention.DECREASE_CALORIES: "Decrease Calories",
            ScenarioIntervention.HIGHER_SLEEP: "Higher Sleep",
            ScenarioIntervention.LOWER_SLEEP: "Lower Sleep",
            ScenarioIntervention.HIGHER_ADHERENCE: "Higher Adherence",
            ScenarioIntervention.LOWER_ADHERENCE: "Lower Adherence",
        }[self]


@dataclass
class ScenarioComparison:
    intervention: ScenarioIntervention = ScenarioIntervention.INCREASE_VOLUME
    baseline_value: float = 0.0
    scenario_value: float = 0.0
    delta: float = 0.0
    delta_percent: float = 0.0
    confidence: PredictionConfidence = field(default_factory=PredictionConfidence)
    description: str = ""
    is_positive: bool = True

    def __post_init__(self) -> None:
        self.delta = self.scenario_value - self.baseline_value
        self.delta_percent = (self.delta / self.baseline_value * 100) if self.baseline_value != 0 else 0.0
        self.is_positive = self.delta >= 0


@dataclass
class ScenarioResult:
    intervention: ScenarioIntervention = ScenarioIntervention.INCREASE_VOLUME
    comparisons: list[ScenarioComparison] = field(default_factory=list)
    overall_assessment: str = ""
    recommended: bool = False
    risk_level: str = "moderate"
    confidence: PredictionConfidence = field(default_factory=PredictionConfidence)


@dataclass
class ScenarioRanking:
    rankings: list[tuple[ScenarioIntervention, float]] = field(default_factory=list)
    top_intervention: ScenarioIntervention | None = None
    top_score: float = 0.0

    def __post_init__(self) -> None:
        if self.rankings:
            self.rankings.sort(key=lambda x: x[1], reverse=True)
            self.top_intervention = self.rankings[0][0]
            self.top_score = self.rankings[0][1]


# ─── Counterfactual Engine Entities ──────────────────────


class CounterfactualType(Enum):
    SLEEP = "sleep"
    CALORIES = "calories"
    WORKOUT_MISS = "workout_miss"
    VOLUME_CHANGE = "volume_change"
    DELOAD_NOW = "deload_now"


@dataclass
class CounterfactualQuery:
    cf_type: CounterfactualType = CounterfactualType.SLEEP
    parameter: str = ""
    current_value: float = 0.0
    proposed_value: float = 0.0
    unit: str = ""


@dataclass
class CounterfactualResult:
    query: CounterfactualQuery = field(default_factory=CounterfactualQuery)
    baseline_prediction: float = 0.0
    counterfactual_prediction: float = 0.0
    absolute_delta: float = 0.0
    percent_delta: float = 0.0
    direction: str = "no_change"
    impact_level: str = "low"
    explanation: str = ""
    affected_predictions: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.absolute_delta = self.counterfactual_prediction - self.baseline_prediction
        self.percent_delta = (self.absolute_delta / self.baseline_prediction * 100) if self.baseline_prediction != 0 else 0.0
        self.direction = "increase" if self.absolute_delta > 0 else ("decrease" if self.absolute_delta < 0 else "no_change")
        if abs(self.percent_delta) >= 20:
            self.impact_level = "high"
        elif abs(self.percent_delta) >= 10:
            self.impact_level = "moderate"
        else:
            self.impact_level = "low"


# ─── Risk Engine Entities ────────────────────────────────


@dataclass
class RiskMetrics:
    stability: float = 0.0
    sensitivity: float = 0.0
    uncertainty: float = 0.0
    confidence_interval_width: float = 0.0
    volatility: float = 0.0
    overall_risk_score: float = 0.0
    risk_level: str = "low"

    def __post_init__(self) -> None:
        self.overall_risk_score = self.stability * 0.25 + self.sensitivity * 0.20 + self.uncertainty * 0.25 + self.volatility * 0.30
        self.overall_risk_score = min(self.overall_risk_score, 1.0)
        if self.overall_risk_score >= 0.7:
            self.risk_level = "high"
        elif self.overall_risk_score >= 0.4:
            self.risk_level = "moderate"
        else:
            self.risk_level = "low"


# ─── Updated PredictionResult ────────────────────────────


@dataclass
class PredictionResult:
    predictions: list[Prediction] = field(default_factory=list)
    generated_at: str = ""
    athlete_id: str = ""
    total_predictions: int = 0
    scenario_results: list[ScenarioResult] = field(default_factory=list)
    counterfactual_results: list[CounterfactualResult] = field(default_factory=list)
    explainability: dict[str, ExplainabilityDetail] = field(default_factory=dict)
    risk_metrics: dict[str, RiskMetrics] = field(default_factory=dict)
    scenario_rankings: ScenarioRanking | None = None

    def __post_init__(self) -> None:
        self.total_predictions = len(self.predictions)
