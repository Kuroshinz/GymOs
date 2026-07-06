from __future__ import annotations

from typing import Any

from ui.narrative.engine import Narrative


def recovery_summary(
    recovery_score: float | None = None,
    sleep_hours: float | None = None,
    sleep_quality: str | None = None,
    hrv: float | None = None,
    muscle_soreness: str | None = None,
    trend: str | None = None,
    **kwargs: Any,
) -> Narrative:
    detail_parts = []
    actions = []

    if recovery_score is not None:
        detail_parts.append(f"Recovery: {recovery_score:.0f}/100.")
    if sleep_hours is not None:
        detail_parts.append(f"Sleep: {sleep_hours:.1f}h ({sleep_quality or 'moderate'}).")
    if hrv is not None:
        detail_parts.append(f"HRV: {hrv:.0f} ms.")
    if muscle_soreness:
        detail_parts.append(f"Soreness: {muscle_soreness}.")
    if trend:
        detail_parts.append(f"Trend: {trend}.")

    if recovery_score is not None:
        if recovery_score >= 80:
            summary = "Fully recovered. Ready to perform at your best."
        elif recovery_score >= 60:
            summary = "Adequately recovered. You can train but watch intensity."
        else:
            summary = "Still under-recovered. Consider lighter work or rest."
    else:
        summary = "Recovery status available."

    if recovery_score is not None and recovery_score < 60:
        actions.append("Reduce training volume by 20–30% today.")
    if sleep_hours is not None and sleep_hours < 6:
        actions.append("Prioritise sleep. Consider a nap or earlier bedtime.")
    if muscle_soreness and "high" in muscle_soreness.lower():
        actions.append("High soreness — foam rolling and light mobility recommended.")

    return Narrative(
        title="Recovery Summary",
        summary=summary,
        body=". ".join(detail_parts) if detail_parts else summary,
        action_items=actions,
        source_keys=["recovery_score", "sleep_hours", "hrv", "muscle_soreness"],
    )
