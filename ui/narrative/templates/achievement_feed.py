from __future__ import annotations

from typing import Any

from ui.narrative.engine import Narrative


def achievement_feed(
    achievements: list[dict[str, Any]] | None = None,
    **kwargs: Any,
) -> Narrative:
    if not achievements:
        return Narrative(
            title="Achievement Feed",
            summary="No recent achievements.",
            source_keys=["achievements"],
        )

    body_parts = []
    detail_parts = []

    for i, ach in enumerate(achievements):
        name = ach.get("name", f"Achievement {i + 1}")
        desc = ach.get("description", "")
        points = ach.get("points", 0)
        date = ach.get("date", "")

        line = f"{name}"
        if points:
            line += f" ({points} pts)"
        if desc:
            line += f" — {desc}"
        body_parts.append(line)

        detail_parts.append(f"{'[' + date + '] ' if date else ''}{name}: {desc} ({points} pts)")

    total_pts = sum(a.get("points", 0) for a in achievements)

    return Narrative(
        title=f"Achievement Feed ({len(achievements)})",
        summary=f"{len(achievements)} new achievement(s). {total_pts} total points earned.",
        body="\n".join(body_parts),
        detail="\n".join(detail_parts),
        action_items=[f"View all {len(achievements)} achievements in your profile."],
        source_keys=["achievements"],
    )
