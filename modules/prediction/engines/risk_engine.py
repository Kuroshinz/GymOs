"""Risk Engine — computes risk metrics for predictions and forecasts.

Metrics:
  - Stability:   How stable the prediction is across its forecast window
  - Sensitivity: How sensitive the prediction is to input perturbations
  - Uncertainty: Total uncertainty (variance + confidence decay)
  - Confidence Interval: Width of the 95% CI
  - Volatility:  How volatile the forecast trajectory is
"""

from __future__ import annotations

from modules.prediction.domain import (
    Forecast,
    Prediction,
    RiskMetrics,
)


class RiskEngine:
    """Computes RiskMetrics for predictions and forecasts."""

    def analyze_prediction(self, prediction: Prediction) -> RiskMetrics:
        stability = self._compute_stability(prediction)
        sensitivity = self._compute_sensitivity(prediction)
        uncertainty = self._compute_uncertainty(prediction)
        ci_width = self._compute_ci_width(prediction)
        volatility = self._compute_volatility(prediction)
        return RiskMetrics(
            stability=round(stability, 4),
            sensitivity=round(sensitivity, 4),
            uncertainty=round(uncertainty, 4),
            confidence_interval_width=round(ci_width, 4),
            volatility=round(volatility, 4),
        )

    def analyze_forecast(self, forecast: Forecast) -> RiskMetrics:
        stability = self._compute_forecast_stability(forecast)
        sensitivity = 0.3  # Default for forecast-only analysis
        uncertainty = self._compute_forecast_uncertainty(forecast)
        ci_width = self._compute_forecast_ci_width(forecast)
        volatility = self._compute_forecast_volatility(forecast)
        return RiskMetrics(
            stability=round(stability, 4),
            sensitivity=round(sensitivity, 4),
            uncertainty=round(uncertainty, 4),
            confidence_interval_width=round(ci_width, 4),
            volatility=round(volatility, 4),
        )

    def _compute_stability(self, prediction: Prediction) -> float:
        factors = [
            prediction.confidence.score * 0.4,
            min(prediction.confidence.sample_size / 20.0, 1.0) * 0.3,
            prediction.confidence.data_quality * 0.3,
        ]
        raw = sum(factors)
        return 1.0 - min(raw, 1.0)

    def _compute_sensitivity(self, prediction: Prediction) -> float:
        evidence = prediction.explanation.evidence
        if not evidence:
            return 0.5
        avg_relevance = sum(e.relevance for e in evidence) / len(evidence)
        evidence_count_factor = min(len(evidence) / 10.0, 1.0)
        raw = (1.0 - avg_relevance) * 0.6 + (1.0 - evidence_count_factor) * 0.4
        return min(raw, 1.0)

    def _compute_uncertainty(self, prediction: Prediction) -> float:
        variance_factor = min(prediction.confidence.variance / 100.0, 1.0) * 0.5
        inv_confidence = (1.0 - prediction.confidence.score) * 0.3
        sample_size_factor = max(0.0, 1.0 - prediction.confidence.sample_size / 30.0) * 0.2
        raw = variance_factor + inv_confidence + sample_size_factor
        return min(raw, 1.0)

    def _compute_ci_width(self, prediction: Prediction) -> float:
        if not prediction.forecast or not prediction.forecast.points:
            return prediction.confidence.variance / 10.0 if prediction.confidence.variance > 0 else 0.1

        mid_point = len(prediction.forecast.points) // 2
        pt = prediction.forecast.points[mid_point]
        width = pt.upper_bound - pt.lower_bound
        normalized = width / (abs(pt.predicted_value) + 1.0)
        return min(normalized, 2.0)

    def _compute_volatility(self, prediction: Prediction) -> float:
        if not prediction.forecast or len(prediction.forecast.points) < 3:
            return 0.0

        values = [p.predicted_value for p in prediction.forecast.points]
        n = len(values)
        if n < 2:
            return 0.0
        avg = sum(values) / n
        if avg == 0:
            return 0.0
        variance = sum((v - avg) ** 2 for v in values) / n
        std_dev = variance ** 0.5
        cv = std_dev / abs(avg)
        return min(cv, 1.0)

    def _compute_forecast_stability(self, forecast: Forecast) -> float:
        points = forecast.points
        if len(points) < 3:
            return 0.5
        values = [p.predicted_value for p in points]
        first_half = values[:len(values) // 2]
        second_half = values[len(values) // 2:]
        avg_first = sum(first_half) / len(first_half) if first_half else 0
        avg_second = sum(second_half) / len(second_half) if second_half else 0
        direction_change = abs(avg_second - avg_first) / (abs(avg_first) + 1.0)
        return min(direction_change, 1.0)

    def _compute_forecast_uncertainty(self, forecast: Forecast) -> float:
        if not forecast.points:
            return 0.5
        avg_confidence = sum(p.confidence_at_point for p in forecast.points) / len(forecast.points)
        return 1.0 - avg_confidence

    def _compute_forecast_ci_width(self, forecast: Forecast) -> float:
        if not forecast.points:
            return 0.1
        widths = [(p.upper_bound - p.lower_bound) / (abs(p.predicted_value) + 1.0) for p in forecast.points]
        return min(sum(widths) / len(widths), 2.0)

    def _compute_forecast_volatility(self, forecast: Forecast) -> float:
        if len(forecast.points) < 3:
            return 0.0
        values = [p.predicted_value for p in forecast.points]
        n = len(values)
        avg = sum(values) / n
        if avg == 0:
            return 0.0
        variance = sum((v - avg) ** 2 for v in values) / n
        std_dev = variance ** 0.5
        cv = std_dev / abs(avg)
        return min(cv, 1.0)
