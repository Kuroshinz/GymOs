from __future__ import annotations

from typing import Any

from ui.narrative.engine import Narrative


def today_focus(
    primary_goal: str | None = None,
    workout_type: str | None = None,
    focus_areas: list[str] | None = None,
    intensity: str | None = None,
    duration_minutes: int | None = None,
    week_day: int | None = None,
    **kwargs: Any,
) -> Narrative:
    detail_parts = []
    actions = []

    if focus_areas:
        areas_str = ", ".join(focus_areas)
        detail_parts.append(f"Focus areas: {areas_str}.")

    if intensity:
        detail_parts.append(f"Target intensity: {intensity}.")
    if duration_minutes:
        detail_parts.append(f"Estimated duration: {duration_minutes} minutes.")
    if workout_type:
        detail_parts.append(f"Workout type: {workout_type}.")

    wday_names = ["", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    wday_str = wday_names[week_day] if week_day and 1 <= week_day <= 7 else ""

    if workout_type:
        actions.append(f"Complete: {workout_type}.")
        if intensity:
            actions.append(f"Maintain {intensity} intensity throughout.")
    if focus_areas:
        actions.append(f"Emphasise: {', '.join(focus_areas)}.")

    title_parts = ["Today's Focus"]
    if wday_str:
        title_parts.append(f"— {wday_str}")
    base = primary_goal or workout_type or "training session"
    title = " ".join(title_parts)

    return Narrative(
        title=title,
        summary=f"Today: {base}." + (f" {areas_str}." if focus_areas else ""),
        body=". ".join(detail_parts) if detail_parts else f"Today's focus is {base}.",
        action_items=actions,
        source_keys=["primary_goal", "workout_type", "focus_areas"],
    )
