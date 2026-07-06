"""NotificationPolicy — suppress low-value, surface high-value notifications.

Deterministic rules based on signal thresholds and user context.
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.cognitive.attention import AttentionItem


@dataclass
class NotificationDecision:
    """Decision for a single notification candidate."""
    should_show: bool
    reason: str = ""
    priority_score: float = 0.0


class NotificationPolicy:
    """Deterministic notification suppression and promotion rules."""

    @staticmethod
    def evaluate(item: AttentionItem, context_tags: list[str]) -> NotificationDecision:
        score = item.score
        tags = set(context_tags)

        if score >= 80:
            return NotificationDecision(
                should_show=True,
                reason=f"High-priority signal ({item.signal.value})",
                priority_score=score,
            )

        suppressed = False
        reason = ""

        if score < 30:
            suppressed = True
            reason = "score below minimum threshold"

        if "recovery-critical" in tags and score < 60:
            suppressed = True
            reason = "suppressed by higher-priority recovery signals"

        if "has-achievements" in tags and item.signal.value == "pr_achieved":
            pass  # Always show achievements

        if "recovery-critical" in tags and item.signal.value == "knowledge_update":
            suppressed = True
            reason = "knowledge updates suppressed while recovery is critical"

        if "fatigue-high" in tags and item.signal.value == "prediction_confidence":
            suppressed = True
            reason = "predictions suppressed while fatigue is high"

        return NotificationDecision(
            should_show=not suppressed,
            reason=reason or "passed all filters",
            priority_score=score if not suppressed else 0.0,
        )

    @staticmethod
    def filter_all(items: list[AttentionItem], context_tags: list[str]) -> list[tuple[AttentionItem, NotificationDecision]]:
        results: list[tuple[AttentionItem, NotificationDecision]] = []
        for item in items:
            decision = NotificationPolicy.evaluate(item, context_tags)
            results.append((item, decision))
        results.sort(key=lambda x: x[1].priority_score, reverse=True)
        return results

    @staticmethod
    def visible_count(results: list[tuple[AttentionItem, NotificationDecision]]) -> int:
        return sum(1 for _, d in results if d.should_show)

    @staticmethod
    def suppressed_count(results: list[tuple[AttentionItem, NotificationDecision]]) -> int:
        return sum(1 for _, d in results if not d.should_show)
