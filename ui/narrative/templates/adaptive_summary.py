from __future__ import annotations

from typing import Any

from ui.narrative.engine import Narrative


def adaptive_summary(
    adaptation_type: str | None = None,
    description: str | None = None,
    reason: str | None = None,
    impact: str | None = None,
    applied: bool | None = None,
    **kwargs: Any,
) -> Narrative:
    detail_parts = []
    actions = []

    if adaptation_type:
        detail_parts.append(f"Type: {adaptation_type}.")
    if description:
        detail_parts.append(description)
    if reason:
        detail_parts.append(f"Why: {reason}.")
    if impact:
        detail_parts.append(f"Impact: {impact}.")

    status = "Applied" if applied else "Recommended"
    summary = f"{status}: {description or adaptation_type or 'adaptive change'}."
    if applied:
        actions.append(f"New adjustment active: {description or adaptation_type}.")
    else:
        actions.append(f"Consider: {description or adaptation_type}.")

    return Narrative(
        title=f"Adaptation: {adaptation_type}" if adaptation_type else "Adaptive Summary",
        summary=summary,
        body=". ".join(detail_parts) if detail_parts else summary,
        action_items=actions,
        source_keys=["adaptation_type", "description", "reason", "impact"],
    )
