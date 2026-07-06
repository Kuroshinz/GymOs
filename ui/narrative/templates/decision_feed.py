from __future__ import annotations

from typing import Any

from ui.narrative.engine import Narrative


def decision_feed(
    decisions: list[dict[str, Any]] | None = None,
    **kwargs: Any,
) -> Narrative:
    if not decisions:
        return Narrative(
            title="Decision Feed",
            summary="No recent decisions.",
            source_keys=["decisions"],
        )

    body_parts = []
    detail_parts = []
    actions = []

    for i, dec in enumerate(decisions):
        title = dec.get("title", f"Decision {i + 1}")
        desc = dec.get("description", "")
        status = dec.get("status", "recommended")
        reason = dec.get("reason", "")
        icon = {"applied": "✓", "dismissed": "✗", "recommended": "→"}.get(status, "•")

        body_parts.append(f"{icon} {title}: {desc}")
        detail_parts.append(f"{icon} {title} [{status}]: {desc}" + (f" Reason: {reason}" if reason else ""))

        if status == "recommended":
            actions.append(f"Review: {title}.")

    applied_count = sum(1 for d in decisions if d.get("status") == "applied")
    recommended_count = sum(1 for d in decisions if d.get("status") == "recommended")

    return Narrative(
        title=f"Decision Feed ({len(decisions)})",
        summary=f"{applied_count} applied, {recommended_count} pending review.",
        body="\n".join(body_parts),
        detail="\n".join(detail_parts),
        action_items=actions,
        source_keys=["decisions"],
    )
