from __future__ import annotations

from typing import Any

from ui.narrative.engine import Narrative


def knowledge_summary(
    topic: str | None = None,
    insight: str | None = None,
    source: str | None = None,
    relevance: str | None = None,
    tags: list[str] | None = None,
    **kwargs: Any,
) -> Narrative:
    detail_parts = []
    actions = []

    if topic:
        detail_parts.append(f"Topic: {topic}.")
    if insight:
        detail_parts.append(insight)
    if source:
        detail_parts.append(f"Source: {source}.")
    if relevance:
        detail_parts.append(f"Relevance: {relevance}.")
    if tags:
        detail_parts.append(f"Tags: {', '.join(tags)}.")

    summary = f"Insight: {insight}" if insight else (f"Knowledge summary for {topic}." if topic else "Knowledge summary available.")
    if relevance:
        actions.append(f"Apply: {relevance}.")
    if source:
        actions.append(f"Review source: {source}.")

    return Narrative(
        title=f"Knowledge: {topic}" if topic else "Knowledge Summary",
        summary=summary,
        body=". ".join(detail_parts) if detail_parts else summary,
        action_items=actions,
        source_keys=["topic", "insight", "relevance", "tags"],
    )
