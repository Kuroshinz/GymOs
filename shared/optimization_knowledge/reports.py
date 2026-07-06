"""Optimization Knowledge Reports — Generates human-readable reports from accumulated knowledge."""

from __future__ import annotations

from shared.optimization_knowledge.domain import (
    KnowledgeConfig,
    KnowledgeState,
    OptimizationKnowledge,
    PatternType,
)
from shared.optimization_knowledge.metrics import KnowledgeMetrics, KnowledgeMetricsResult


class KnowledgeReportGenerator:
    """Generates human-readable reports from accumulated knowledge."""

    def __init__(self, config: KnowledgeConfig = KnowledgeConfig()) -> None:
        self.config = config
        self.metrics = KnowledgeMetrics(config)

    def generate_summary_report(
        self,
        knowledge: OptimizationKnowledge,
    ) -> str:
        lines: list[str] = [
            "=" * 60,
            "  OPTIMIZATION KNOWLEDGE SUMMARY REPORT",
            "=" * 60,
            "",
            f"Knowledge Version: {knowledge.version}",
            f"Parent Version:    {knowledge.parent_version or '(none)'}",
            f"Generated:         {knowledge.updated_at or knowledge.created_at}",
            "",
            "--- Experience Summary ---",
            f"  Total Experiences: {len(knowledge.experiences)}",
            f"  Total Patterns:    {len(knowledge.patterns)}",
            f"  Total Insights:    {len(knowledge.insights)}",
            f"  Total Rules:       {len(knowledge.rules)}",
            f"  Total Recommendations: {len(knowledge.recommendations)}",
            "",
            "--- Statistics ---",
        ]

        if knowledge.statistics:
            s = knowledge.statistics[0]
            lines.extend([
                f"  Mean Score:    {s.mean_score:.4f}",
                f"  Median Score:  {s.median_score:.4f}",
                f"  Success Rate:  {s.success_rate:.2%}",
                f"  Std Dev:       {s.std_dev_score:.4f}",
                f"  CI (95%):      [{s.confidence_interval_lower:.4f}, {s.confidence_interval_upper:.4f}]",
                f"  Trend:         {s.trend_direction} (slope: {s.trend_slope:.4f})",
                f"  Moving Avg (5): {s.moving_average:.4f}",
            ])
        else:
            lines.append("  (no statistics computed)")

        lines.append("")
        lines.append("--- Top Patterns by Success Rate ---")
        top_patterns = sorted(
            knowledge.patterns,
            key=lambda p: p.success_rate,
            reverse=True,
        )[:5]
        if top_patterns:
            for p in top_patterns:
                reliable = "RELIABLE" if (
                    p.sample_size >= 10 and p.confidence >= 0.8
                ) else "low sample"
                lines.append(
                    f"  [{p.pattern_type.value.upper()}] {p.label}: "
                    f"{p.success_rate:.1%} success (n={p.sample_size}, "
                    f"conf={p.confidence:.2f}, {reliable})"
                )
        else:
            lines.append("  (no patterns mined)")

        lines.append("")
        lines.append("--- Rules ---")
        if knowledge.rules:
            for r in knowledge.rules[:5]:
                lines.append(
                    f"  [{r.pattern_type.value.upper()}] {r.effect.value}: "
                    f"{r.condition} (conf={r.confidence:.2f})"
                )
        else:
            lines.append("  (no rules derived)")

        lines.append("")
        lines.append("--- Recommendations ---")
        if knowledge.recommendations:
            for rec in knowledge.recommendations[:5]:
                lines.append(
                    f"  [{rec.pattern_type.value.upper()}] {rec.title}: "
                    f"value {rec.suggested_value_min}-{rec.suggested_value_max}, "
                    f"improvement {rec.expected_improvement:.2f}"
                )
        else:
            lines.append("  (no recommendations)")

        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)

    def generate_detailed_report(
        self,
        knowledge: OptimizationKnowledge,
    ) -> str:
        lines: list[str] = [
            "=" * 60,
            "  OPTIMIZATION KNOWLEDGE DETAILED REPORT",
            "=" * 60,
            "",
            f"Knowledge Version: {knowledge.version}",
            f"Generated:         {knowledge.updated_at or knowledge.created_at}",
            "",
        ]

        metrics_result = self.metrics.compute_metrics(knowledge)
        lines.extend(self._format_metrics(metrics_result))

        lines.append("")
        lines.append("--- All Patterns ---")
        for ptype in PatternType:
            type_patterns = [
                p for p in knowledge.patterns
                if p.pattern_type == ptype
            ]
            if type_patterns:
                lines.append(f"\n  [{ptype.value.upper()}]")
                for p in sorted(type_patterns, key=lambda x: x.success_rate, reverse=True):
                    lines.append(
                        f"    {p.label}: {p.success_rate:.1%} success "
                        f"(n={p.sample_size}, conf={p.confidence:.2f})"
                    )

        lines.append("")
        lines.append("--- All Profiles ---")
        if knowledge.profiles:
            for prof in knowledge.profiles:
                lines.extend([
                    f"\n  Goal: {prof.best_goal or '(no goal)'}",
                    f"    Best Sessions/Week: {prof.best_sessions_per_week}",
                    f"    Best Total Weeks:   {prof.best_total_weeks}",
                    f"    Best Avg Weekly Sets: {prof.best_avg_weekly_sets:.1f}",
                    f"    Best Split:         {prof.best_split_style or '(none)'}",
                    f"    Best Mesocycles:    {prof.best_mesocycle_count}",
                    f"    Avg Success Rate:   {prof.avg_success_rate:.2%}",
                ])
        else:
            lines.append("  (no profiles built)")

        lines.append("")
        lines.append("--- All Insights ---")
        if knowledge.insights:
            for ins in knowledge.insights:
                lines.append(
                    f"  [{ins.category.value}] {ins.title}: {ins.description} "
                    f"(conf={ins.confidence:.2f})"
                )
        else:
            lines.append("  (no insights generated)")

        lines.append("")
        lines.append("--- All Rules ---")
        if knowledge.rules:
            for r in knowledge.rules:
                lines.append(
                    f"  [{r.pattern_type.value.upper()}] {r.effect.value}: "
                    f"{r.condition} (conf={r.confidence:.2f}, n={r.sample_size})"
                )
        else:
            lines.append("  (no rules derived)")

        lines.append("")
        lines.append("--- All Recommendations ---")
        if knowledge.recommendations:
            for rec in knowledge.recommendations:
                lines.append(
                    f"  [{rec.pattern_type.value.upper()}] {rec.title}: "
                    f"value {rec.suggested_value_min}-{rec.suggested_value_max}, "
                    f"improvement {rec.expected_improvement:.2f}, "
                    f"conf={rec.confidence:.2f}"
                )
        else:
            lines.append("  (no recommendations)")

        lines.append("")
        lines.append("=" * 60)
        return "\n".join(lines)

    def generate_state_report(self, state: KnowledgeState) -> str:
        lines: list[str] = [
            "=" * 60,
            "  OPTIMIZATION KNOWLEDGE STATE REPORT",
            "=" * 60,
            "",
            f"Current Version: {state.current_version or '(none)'}",
            f"Total Versions:  {state.total_versions}",
            "",
            "--- Knowledge State ---",
            f"  Total Experiences: {state.total_experiences}",
            f"  Total Patterns:    {state.total_patterns}",
            f"  Total Insights:    {state.total_insights}",
            f"  Total Rules:       {state.total_rules}",
            f"  Global Success Rate: {state.global_success_rate:.2%}",
            f"  Global Mean Score:   {state.global_mean_score:.4f}",
            "",
            "=" * 60,
        ]
        return "\n".join(lines)

    @staticmethod
    def _format_metrics(m: KnowledgeMetricsResult) -> list[str]:
        return [
            "--- Quality Metrics ---",
            f"  Total Patterns:           {m.total_patterns}",
            f"  Reliable Patterns:        {m.reliable_patterns}",
            f"  High Confidence Patterns:  {m.high_confidence_patterns}",
            f"  Low Sample Patterns:       {m.low_sample_patterns}",
            f"  Pattern Type Coverage:     {m.pattern_type_coverage} ({m.coverage_ratio:.1%})",
            f"  Avg Confidence:           {m.avg_confidence:.3f}",
            f"  Avg Success Rate:         {m.avg_success_rate:.3f}",
            f"  Avg Redundancy:           {m.avg_redundancy:.3f}",
        ]
