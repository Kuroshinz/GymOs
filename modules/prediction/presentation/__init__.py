from __future__ import annotations

from dataclasses import dataclass, field

from modules.prediction.domain import (
    ConfidenceLevel,
    Prediction,
    PredictionResult,
    PredictionType,
    PredictionWindow,
)


@dataclass
class PredictionWidgetData:
    label: str = ""
    value: str = ""
    probability: str = ""
    confidence: str = ""
    trend_direction: str = ""
    summary: str = ""
    score_color: str = "#94A3B8"
    has_data: bool = False


@dataclass
class ForecastPointData:
    date: str = ""
    predicted: float = 0.0
    lower: float = 0.0
    upper: float = 0.0
    confidence: float = 0.0


@dataclass
class ForecastTimelineData:
    points: list[ForecastPointData] = field(default_factory=list)
    prediction_type: str = ""
    window_label: str = ""


@dataclass
class RiskTimelineData:
    date: str = ""
    risk_level: str = ""
    risk_score: float = 0.0
    description: str = ""


@dataclass
class PredictionViewModel:
    pr_prediction: PredictionWidgetData = field(default_factory=PredictionWidgetData)
    plateau_prediction: PredictionWidgetData = field(default_factory=PredictionWidgetData)
    recovery_forecast: PredictionWidgetData = field(default_factory=PredictionWidgetData)
    bodyweight_forecast: PredictionWidgetData = field(default_factory=PredictionWidgetData)
    goal_eta: PredictionWidgetData = field(default_factory=PredictionWidgetData)
    mrv_risk: PredictionWidgetData = field(default_factory=PredictionWidgetData)
    deload_probability: PredictionWidgetData = field(default_factory=PredictionWidgetData)
    consistency_forecast: PredictionWidgetData = field(default_factory=PredictionWidgetData)
    forecast_timelines: list[ForecastTimelineData] = field(default_factory=list)
    risk_timeline: list[RiskTimelineData] = field(default_factory=list)
    has_data: bool = False


    @staticmethod
    def impact_level_color(impact: str) -> str:
        colors = {"high": "#EF4444", "moderate": "#FBBF24", "low": "#4ADE80"}
        return colors.get(impact, "#94A3B8")

    @staticmethod
    def risk_level_color(risk: str) -> str:
        colors = {"high": "#EF4444", "moderate": "#FBBF24", "low": "#4ADE80"}
        return colors.get(risk, "#94A3B8")

    @staticmethod
    def direction_icon(direction: str) -> str:
        icons = {"increase": "▲", "decrease": "▼", "positive": "▲", "negative": "▼", "no_change": "◆"}
        return icons.get(direction, "◆")


class PredictionFormatter:
    @staticmethod
    def impact_level_color(impact: str) -> str:
        colors = {"high": "#EF4444", "moderate": "#FBBF24", "low": "#4ADE80"}
        return colors.get(impact, "#94A3B8")

    @staticmethod
    def risk_level_color(risk: str) -> str:
        colors = {"high": "#EF4444", "moderate": "#FBBF24", "low": "#4ADE80"}
        return colors.get(risk, "#94A3B8")

    @staticmethod
    def format_percentage(value: float) -> str:
        return f"{value:.0f}%"

    @staticmethod
    def format_decimal(value: float, decimals: int = 1) -> str:
        return f"{value:.{decimals}f}"

    @staticmethod
    def format_bodyweight(kg: float) -> str:
        return f"{kg:.1f}kg"

    @staticmethod
    def format_days(days: float) -> str:
        if days >= 365:
            return f"{days / 365:.1f}y"
        if days >= 30:
            return f"{days / 30:.1f}mo"
        return f"{int(days)}d"

    @staticmethod
    def format_date(date_str: str) -> str:
        return date_str

    @staticmethod
    def get_confidence_color(confidence: ConfidenceLevel) -> str:
        colors = {
            ConfidenceLevel.VERY_HIGH: "#4ADE80",
            ConfidenceLevel.HIGH: "#86EFAC",
            ConfidenceLevel.MODERATE: "#FBBF24",
            ConfidenceLevel.LOW: "#FB923C",
            ConfidenceLevel.VERY_LOW: "#EF4444",
        }
        return colors.get(confidence, "#94A3B8")

    @staticmethod
    def get_risk_color(probability: float) -> str:
        if probability >= 0.7:
            return "#EF4444"
        if probability >= 0.4:
            return "#FBBF24"
        return "#4ADE80"

    @staticmethod
    def get_trend_icon(trend: str) -> str:
        icons = {"increasing": "▲", "decreasing": "▼", "stable": "◆"}
        return icons.get(trend, "◆")

    @staticmethod
    def get_prediction_label(ptype: PredictionType) -> str:
        return ptype.label

    @staticmethod
    def get_window_label(window: PredictionWindow) -> str:
        return window.label

    @staticmethod
    def prediction_to_widget_data(prediction: Prediction | None) -> PredictionWidgetData:
        if prediction is None:
            return PredictionWidgetData()
        trend = prediction.forecast.direction if prediction.forecast else "stable"
        return PredictionWidgetData(
            label=prediction.prediction_type.label,
            value=f"{prediction.value:.0f}"
                       if prediction.prediction_type != PredictionType.GOAL_ETA
                       else PredictionFormatter.format_days(prediction.value),
            probability=PredictionFormatter.format_percentage(prediction.probability * 100),
            confidence=f"{prediction.confidence.level.label} ({prediction.confidence.score:.0%})",
            trend_direction=trend,
            summary=prediction.explanation.summary,
            score_color=PredictionFormatter.get_risk_color(prediction.probability),
            has_data=True,
        )

    @staticmethod
    def prediction_result_to_view_model(result: PredictionResult) -> PredictionViewModel:
        vm = PredictionViewModel(has_data=len(result.predictions) > 0)
        for pred in result.predictions:
            widget = PredictionFormatter.prediction_to_widget_data(pred)
            if pred.prediction_type == PredictionType.NEXT_PR_PROBABILITY:
                vm.pr_prediction = widget
            elif pred.prediction_type == PredictionType.PLATEAU_PROBABILITY:
                vm.plateau_prediction = widget
            elif pred.prediction_type == PredictionType.RECOVERY_DECLINE:
                vm.recovery_forecast = widget
            elif pred.prediction_type == PredictionType.BODYWEIGHT_TREND:
                vm.bodyweight_forecast = widget
            elif pred.prediction_type == PredictionType.GOAL_ETA:
                vm.goal_eta = widget
            elif pred.prediction_type == PredictionType.MRV_VIOLATION_RISK:
                vm.mrv_risk = widget
            elif pred.prediction_type == PredictionType.DELOAD_PROBABILITY:
                vm.deload_probability = widget
            elif pred.prediction_type == PredictionType.CONSISTENCY_DECAY:
                vm.consistency_forecast = widget

            if pred.forecast:
                timeline = ForecastTimelineData(
                    points=[
                        ForecastPointData(
                            date=p.date, predicted=p.predicted_value,
                            lower=p.lower_bound, upper=p.upper_bound,
                            confidence=p.confidence_at_point,
                        )
                        for p in pred.forecast.points
                    ],
                    prediction_type=pred.prediction_type.label,
                    window_label=pred.window.label,
                )
                vm.forecast_timelines.append(timeline)

        return vm
