from __future__ import annotations

from typing import Any

from ui.narrative.engine import Narrative


def milestone_celebration(
    milestone_name: str | None = None,
    milestone_type: str | None = None,
    value: float | None = None,
    target: float | None = None,
    days_early: int | None = None,
    weeks_consistent: int | None = None,
    previous_best: float | None = None,
    **kwargs: Any,
) -> Narrative:
    detail_parts = []
    actions = []

    name = milestone_name or milestone_type or "milestone"
    detail_parts.append(f"Milestone: {name}.")

    if value is not None and target is not None:
        detail_parts.append(f"Value: {value:.1f}/{target:.1f}.")
    elif value is not None:
        detail_parts.append(f"Value: {value:.1f}.")

    if days_early:
        detail_parts.append(f"Achieved {days_early} day(s) early.")
    if weeks_consistent:
        detail_parts.append(f"{weeks_consistent} week(s) of consistency.")
    if previous_best is not None and value is not None:
        delta = value - previous_best
        detail_parts.append(f"{'+' if delta > 0 else ''}{delta:.1f} vs previous best.")

    celebrations = [
        f"Congratulations on reaching {name}!",
        f"You've achieved {name} — keep the momentum going.",
        f"{name} unlocked. Your hard work is paying off.",
    ]
    summary = celebrations[hash(name) % len(celebrations)]

    actions.append("Share this achievement and set your next milestone.")
    if weeks_consistent:
        actions.append(f"Maintain your {weeks_consistent}-week streak.")

    return Narrative(
        title=f"Milestone: {name}",
        summary=summary,
        body=". ".join(detail_parts) if detail_parts else summary,
        action_items=actions,
        source_keys=["milestone_name", "milestone_type", "value", "target", "days_early"],
    )
