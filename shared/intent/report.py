from __future__ import annotations

from shared.intent.domain import UserIntent
from shared.intent.metrics import IntentMetrics
from shared.intent.scorer import IntentScorer
from shared.intent.validator import IntentValidator


class IntentReport:
    @staticmethod
    def generate_report(intents: list[UserIntent], scorer: IntentScorer, validator: IntentValidator) -> str:
        metrics = IntentMetrics.compute(intents, scorer, validator)
        lines: list[str] = []
        lines.append("# Intent Platform Report")
        lines.append("")
        lines.append(f"**Total Intents:** {metrics.total_intents}")
        lines.append(f"**Active:** {metrics.active_intents}  |  **Archived:** {metrics.archived_intents}")
        lines.append("")
        lines.append("## Health Summary")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Overall Health | {metrics.health.overall:.0%} |")
        lines.append(f"| Completeness | {metrics.health.completeness:.0%} |")
        lines.append(f"| Consistency | {metrics.health.consistency:.0%} |")
        lines.append(f"| Confidence | {metrics.health.confidence:.0%} |")
        lines.append(f"| Stability | {metrics.health.stability:.0%} |")
        lines.append(f"| Alignment | {metrics.health.alignment:.0%} |")
        lines.append("")
        lines.append("## Score Distribution")
        lines.append("")
        lines.append("| Metric | Average |")
        lines.append("|--------|--------|")
        lines.append(f"| Overall Score | {metrics.avg_score:.2f} |")
        lines.append(f"| Completeness | {metrics.avg_completeness:.2f} |")
        lines.append(f"| Consistency | {metrics.avg_consistency:.2f} |")
        lines.append(f"| Confidence | {metrics.avg_confidence:.2f} |")
        lines.append(f"| Stability | {metrics.avg_stability:.2f} |")
        lines.append("")
        lines.append("## Conflict Report")
        lines.append("")
        lines.append("| Metric | Count |")
        lines.append("|--------|-------|")
        lines.append(f"| Total Conflicts | {metrics.total_conflicts} |")
        lines.append(f"| Resolved | {metrics.resolved_conflicts} |")
        lines.append(f"| Unresolved | {metrics.unresolved_conflicts} |")
        lines.append("")
        lines.append("## Content Summary")
        lines.append("")
        lines.append("| Metric | Count |")
        lines.append("|--------|-------|")
        lines.append(f"| Total Goals | {metrics.total_goals} |")
        lines.append(f"| Total Constraints | {metrics.total_constraints} |")
        lines.append("")

        for i, intent in enumerate(intents):
            lines.append(f"## Intent {i + 1}: {intent.intent_id or 'Unnamed'}")
            lines.append("")
            s = scorer.score(intent)
            v = validator.validate(intent)
            lines.append(f"- **Score:** {s:.2f}")
            lines.append(f"- **Status:** {intent.status.value}")
            lines.append(f"- **Goals:** {len(intent.goals)}")
            lines.append(f"- **Conflicts:** {len(intent.conflicts)} ({sum(1 for c in intent.conflicts if c.is_resolved)} resolved)")
            lines.append(f"- **Validation:** {'Pass' if v.is_valid else 'Fail'} ({v.error_count} errors, {v.warning_count} warnings)")
            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def generate_summary(intents: list[UserIntent], scorer: IntentScorer) -> str:
        if not intents:
            return "No intents registered."
        scores = [scorer.score(i) for i in intents]
        avg = sum(scores) / len(scores)
        best = max(scores)
        worst = min(scores)
        lines: list[str] = [
            f"Intents: {len(intents)}",
            f"Avg Score: {avg:.2f}",
            f"Best: {best:.2f}",
            f"Worst: {worst:.2f}",
            f"Active: {sum(1 for i in intents if i.status.value == 'active')}",
            f"Archived: {sum(1 for i in intents if i.status.value == 'archived')}",
        ]
        return "\n".join(lines)

    @staticmethod
    def generate_json_report(intents: list[UserIntent], scorer: IntentScorer, validator: IntentValidator) -> dict:
        metrics = IntentMetrics.compute(intents, scorer, validator)
        return {
            "metrics": {
                "total_intents": metrics.total_intents,
                "active_intents": metrics.active_intents,
                "archived_intents": metrics.archived_intents,
                "avg_score": metrics.avg_score,
                "total_conflicts": metrics.total_conflicts,
                "resolved_conflicts": metrics.resolved_conflicts,
                "unresolved_conflicts": metrics.unresolved_conflicts,
                "total_goals": metrics.total_goals,
                "total_constraints": metrics.total_constraints,
            },
            "health": {
                "overall": metrics.health.overall,
                "completeness": metrics.health.completeness,
                "consistency": metrics.health.consistency,
                "confidence": metrics.health.confidence,
                "stability": metrics.health.stability,
                "alignment": metrics.health.alignment,
            },
            "intents": [
                {
                    "id": i.intent_id,
                    "status": i.status.value,
                    "score": scorer.score(i),
                    "goals": len(i.goals),
                    "conflicts": len(i.conflicts),
                    "validation": validator.validate(i).is_valid,
                }
                for i in intents
            ],
        }
