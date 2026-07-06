from __future__ import annotations

from typing import Any

from ui.narrative.engine import Narrative


def prediction_summary(
    prediction_label: str | None = None,
    confidence: float | None = None,
    target_date: str | None = None,
    metric_name: str | None = None,
    current_value: float | None = None,
    predicted_value: float | None = None,
    factors: list[str] | None = None,
    **kwargs: Any,
) -> Narrative:
    detail_parts = []
    actions = []

    label = prediction_label or metric_name or "performance"
    detail_parts.append(f"Prediction: {label}.")
    if predicted_value is not None:
        detail_parts.append(f"Projected: {predicted_value:.1f}.")
    if confidence is not None:
        detail_parts.append(f"Confidence: {confidence:.0f}%.")
    if target_date:
        detail_parts.append(f"Target: {target_date}.")
    if current_value is not None:
        detail_parts.append(f"Current: {current_value:.1f}.")
    if factors:
        detail_parts.append(f"Key factors: {', '.join(factors)}.")

    if confidence is not None and confidence >= 80:
        summary = f"High-confidence prediction: {label}."
    elif confidence is not None and confidence >= 60:
        summary = f"Moderate-confidence prediction: {label}."
    else:
        summary = f"Prediction available for {label}."

    if confidence is not None and confidence >= 80:
        actions.append(f"Tracking towards {label} — stay the course.")
    elif confidence is not None and confidence < 60:
        actions.append("Increase data采集 for better prediction accuracy.")
    if predicted_value is not None and current_value is not None and predicted_value > current_value:
        actions.append(f"On track to improve {metric_name or 'performance'}.")

    return Narrative(
        title="Prediction Summary",
        summary=summary,
        body=". ".join(detail_parts) if detail_parts else summary,
        action_items=actions,
        source_keys=["prediction_label", "confidence", "metric_name"],
    )
