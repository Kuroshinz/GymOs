from __future__ import annotations

from typing import Any

from ui.narrative.engine import Narrative


def morning_brief(
    readiness_score: float | None = None,
    recovery_score: float | None = None,
    fatigue_score: float | None = None,
    sleep_hours: float | None = None,
    hrv: float | None = None,
    today_workout: str | None = None,
    **kwargs: Any,
) -> Narrative:
    items = []
    actions = []

    if readiness_score is not None:
        items.append(f"Readiness: {readiness_score:.0f}/100")
    if recovery_score is not None:
        items.append(f"Recovery: {recovery_score:.0f}/100")
    if fatigue_score is not None:
        items.append(f"Fatigue: {fatigue_score:.0f}/100")
    if sleep_hours is not None:
        items.append(f"Sleep: {sleep_hours:.1f}h")
    if hrv is not None:
        items.append(f"HRV: {hrv:.0f}ms")

    if sleep_hours is not None and sleep_hours < 7:
        actions.append("Prioritise sleep quality tonight — aim for 8+ hours.")
    if fatigue_score is not None and fatigue_score > 70:
        actions.append("High fatigue detected. Consider a deload or active recovery day.")
    if readiness_score is not None and readiness_score < 50:
        actions.append("Low readiness — focus on mobility and light cardio.")
    if today_workout:
        actions.append(f"Scheduled: {today_workout}")

    summary_parts = [f"Ready for today{' — ' + today_workout if today_workout else ''}."]
    if readiness_score is not None:
        if readiness_score >= 80:
            summary_parts.insert(0, "You're primed for peak performance today.")
        elif readiness_score >= 60:
            summary_parts.insert(0, "Solid baseline — push hard but stay mindful.")
        else:
            summary_parts.insert(0, "Take it easy today. Recovery comes first.")
    summary = " ".join(summary_parts)

    body_parts = ["Your morning metrics are in."]
    if readiness_score is not None:
        body_parts.append(f"Readiness sits at {readiness_score:.0f}%, which indicates how well your nervous system has recovered overnight.")
    if recovery_score is not None:
        body_parts.append(f"Recovery is at {recovery_score:.0f}%, reflecting muscle repair and inflammation status.")
    if fatigue_score is not None:
        body_parts.append(f"Fatigue is {fatigue_score:.0f}% — this is your accumulated training load signal.")
    if sleep_hours is not None or hrv is not None:
        detail_parts = []
        if sleep_hours is not None:
            detail_parts.append(f"Sleep duration: {sleep_hours:.1f} hours.")
        if hrv is not None:
            detail_parts.append(f"Heart rate variability: {hrv:.0f} ms (higher is generally better for recovery).")
        body_parts.append(" ".join(detail_parts))

    detail = "\n".join(body_parts)

    return Narrative(
        title="Morning Brief",
        summary=summary,
        body=". ".join(body_parts),
        detail=detail,
        action_items=actions,
        source_keys=["readiness_score", "recovery_score", "fatigue_score", "sleep_hours", "hrv"],
    )
