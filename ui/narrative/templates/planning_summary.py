from __future__ import annotations

from typing import Any

from ui.narrative.engine import Narrative


def planning_summary(
    phase_name: str | None = None,
    week_number: int | None = None,
    total_weeks: int | None = None,
    sessions_this_week: int | None = None,
    sessions_completed: int | None = None,
    volume_change: str | None = None,
    intensity_change: str | None = None,
    focus: str | None = None,
    **kwargs: Any,
) -> Narrative:
    detail_parts = []
    actions = []

    if phase_name:
        detail_parts.append(f"Phase: {phase_name}.")
    if week_number is not None and total_weeks is not None:
        detail_parts.append(f"Week {week_number}/{total_weeks}.")
    if sessions_this_week is not None:
        done = sessions_completed or 0
        detail_parts.append(f"Sessions: {done}/{sessions_this_week} completed.")
    if volume_change:
        detail_parts.append(f"Volume: {volume_change}.")
    if intensity_change:
        detail_parts.append(f"Intensity: {intensity_change}.")
    if focus:
        detail_parts.append(f"Focus: {focus}.")

    phase_str = phase_name or "current"
    summary = f"Week {week_number}/{total_weeks} of {phase_str}." if week_number else f"{phase_str} phase active."
    if sessions_completed is not None and sessions_this_week is not None:
        remaining = sessions_this_week - sessions_completed
        if remaining > 0:
            actions.append(f"{remaining} session(s) remaining this week.")
        else:
            actions.append("All sessions completed — rest and recover.")
    if volume_change:
        actions.append(f"Adjust volume: {volume_change}.")
    if intensity_change:
        actions.append(f"Adjust intensity: {intensity_change}.")

    return Narrative(
        title="Planning Summary",
        summary=summary,
        body=". ".join(detail_parts) if detail_parts else summary,
        action_items=actions,
        source_keys=["phase_name", "week_number", "total_weeks", "sessions_this_week"],
    )
