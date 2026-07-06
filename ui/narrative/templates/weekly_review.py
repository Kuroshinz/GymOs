from __future__ import annotations

from typing import Any

from ui.narrative.engine import Narrative


def weekly_review(
    week_number: int | None = None,
    sessions_completed: int | None = None,
    sessions_planned: int | None = None,
    total_volume: float | None = None,
    volume_change: float | None = None,
    prs_set: int | None = None,
    avg_readiness: float | None = None,
    avg_recovery: float | None = None,
    highlights: list[str] | None = None,
    challenges: list[str] | None = None,
    **kwargs: Any,
) -> Narrative:
    body_parts = []
    detail_parts = []
    actions = []

    week_str = f"Week {week_number}" if week_number else "This week"
    body_parts.append(f"{week_str} review.")

    if sessions_completed is not None and sessions_planned is not None:
        pct = (sessions_completed / sessions_planned * 100) if sessions_planned > 0 else 0
        body_parts.append(f"Completed {sessions_completed}/{sessions_planned} sessions ({pct:.0f}%).")
        detail_parts.append(f"Adherence: {pct:.0f}%.")

    if total_volume is not None:
        body_parts.append(f"Total volume: {total_volume:.0f} kg.")
    if volume_change is not None:
        direction = "increased" if volume_change > 0 else "decreased"
        body_parts.append(f"Volume {direction} by {abs(volume_change):.0f}%.")
    if prs_set is not None and prs_set > 0:
        body_parts.append(f"Personal records set: {prs_set}.")
    if avg_readiness is not None:
        detail_parts.append(f"Average readiness: {avg_readiness:.0f}/100.")
    if avg_recovery is not None:
        detail_parts.append(f"Average recovery: {avg_recovery:.0f}/100.")

    if highlights:
        body_parts.append(f"Highlights: {'; '.join(highlights)}.")
    if challenges:
        body_parts.append(f"Challenges: {'; '.join(challenges)}.")
        actions.extend(challenges)

    if prs_set is not None and prs_set > 0:
        actions.append(f"Celebrate {prs_set} new PR(s) — consistency pays off.")
    if sessions_completed is not None and sessions_planned is not None:
        if sessions_completed < sessions_planned:
            actions.append("Aim to improve adherence next week.")
        else:
            actions.append("Perfect attendance — great consistency.")

    return Narrative(
        title=f"Weekly Review — Week {week_number}" if week_number else "Weekly Review",
        summary=". ".join(body_parts) if body_parts else "Weekly summary available.",
        body="  ".join(body_parts) if body_parts else "",
        detail="  ".join(detail_parts) if detail_parts else "",
        action_items=actions,
        source_keys=["week_number", "sessions_completed", "sessions_planned", "total_volume", "prs_set"],
    )
