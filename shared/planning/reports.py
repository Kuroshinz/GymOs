"""Planning Reports — generates human-readable reports for plans, metrics, and history."""

from __future__ import annotations

from shared.planning.domain import Macrocycle
from shared.planning.metrics import PlanningMetrics, PlanningMetricsScorer, PlanQuality
from shared.planning.validator import PlanningValidator, ValidationResult


class PlanningReports:
    """Generates structured reports from planning data."""

    @staticmethod
    def generate_plan_report(macrocycle: Macrocycle, quality: PlanQuality) -> str:
        lines: list[str] = []
        lines.append(f"# Plan Report: {macrocycle.name}")
        lines.append("")
        lines.append(f"**Macrocycle ID:** {macrocycle.macrocycle_id}")
        lines.append(f"**Duration:** {macrocycle.total_weeks} weeks ({macrocycle.start_date} → {macrocycle.end_date})")
        lines.append(f"**Goal:** {macrocycle.overall_goal}")
        lines.append(f"**Total Sessions:** {macrocycle.total_sessions}")
        lines.append(f"**Total Sets:** {macrocycle.total_sets}")
        lines.append("")
        lines.append("## Quality Assessment")
        lines.append("")
        lines.append("| Metric | Score | Grade |")
        lines.append("|--------|-------|-------|")
        lines.append(f"| Overall | {quality.overall:.0%} | {quality.grade} |")
        lines.append(f"| Scientific Validity | {quality.scientific_score:.0%} | |")
        lines.append(f"| Recovery Balance | {quality.recovery_balance:.0%} | |")
        lines.append(f"| Fatigue Balance | {quality.fatigue_balance:.0%} | |")
        lines.append(f"| Specificity | {quality.specificity:.0%} | |")
        lines.append(f"| Adherence Prediction | {quality.adherence_prediction:.0%} | |")
        lines.append(f"| Volume Distribution | {quality.volume_distribution:.0%} | |")
        lines.append(f"| Progression Quality | {quality.progression_quality:.0%} | |")
        lines.append("")
        lines.append(f"**Overall Grade: {quality.grade}** — {'Acceptable' if quality.is_acceptable else 'Needs improvement'}")
        lines.append("")

        for i, meso in enumerate(macrocycle.mesocycles):
            lines.append(f"## Mesocycle {i + 1}: {meso.name}")
            lines.append("")
            lines.append(f"- **Goal:** {meso.goal.label}")
            lines.append(f"- **Focus:** {meso.focus.label}")
            lines.append(f"- **Phase:** {meso.phase.label}")
            lines.append(f"- **Weeks:** {meso.total_weeks}")
            lines.append(f"- **Intensity Zone:** {meso.intensity_zone.label}")
            lines.append(f"- **Target RIR:** {meso.target_rir}")
            lines.append(f"- **Target RPE:** {meso.target_rpe}")
            lines.append(f"- **Volume Range:** {meso.min_volume_per_muscle}-{meso.max_volume_per_muscle} sets/muscle")
            lines.append("")
            for w in meso.weeks:
                status = "DELOAD" if w.is_deload_week else "TRAINING"
                lines.append(f"  - Week {w.week_number} [{status}]: {w.session_count} sessions, {w.total_sets} sets")

        return "\n".join(lines)

    @staticmethod
    def generate_validation_report(macrocycle: Macrocycle, validation: ValidationResult) -> str:
        lines: list[str] = []
        lines.append(f"# Validation Report: {macrocycle.name}")
        lines.append("")
        lines.append(f"**Status:** {'PASS' if validation.is_valid else 'FAIL'}")
        lines.append(f"**Errors:** {validation.error_count}")
        lines.append(f"**Warnings:** {validation.warning_count}")
        lines.append("")
        if validation.errors:
            lines.append("## Errors")
            lines.append("")
            lines.append("| Field | Message | Code |")
            lines.append("|-------|---------|------|")
            for err in validation.errors:
                lines.append(f"| {err.field} | {err.message} | {err.code} |")
            lines.append("")
        if validation.warnings:
            lines.append("## Warnings")
            lines.append("")
            lines.append("| Field | Message | Code |")
            lines.append("|-------|---------|------|")
            for warn in validation.warnings:
                lines.append(f"| {warn.field} | {warn.message} | {warn.code} |")
            lines.append("")
        return "\n".join(lines)

    @staticmethod
    def generate_summary_report(macrocycle: Macrocycle) -> str:
        lines: list[str] = []
        lines.append(f"# {macrocycle.name} — Summary")
        lines.append("")
        lines.append(f"**Duration:** {macrocycle.duration_weeks} weeks")
        lines.append(f"**Mesocycles:** {macrocycle.total_mesocycles}")
        lines.append(f"**Total Sessions:** {macrocycle.total_sessions}")
        lines.append(f"**Total Sets:** {macrocycle.total_sets}")
        lines.append(f"**Avg Session Volume:** {macrocycle.average_session_volume:.0f} sets")
        lines.append("")
        lines.append("## Mesocycle Progression")
        lines.append("")
        lines.append("| # | Name | Phase | Weeks | Sessions | Total Sets |")
        lines.append("|---|------|-------|-------|----------|------------|")
        for i, m in enumerate(macrocycle.mesocycles):
            lines.append(f"| {i + 1} | {m.name} | {m.phase.label} | {m.total_weeks} | "
                         f"{len(m.sessions)} | {sum(w.total_sets for w in m.weeks)} |")
        lines.append("")
        lines.append("## Weekly Volume Trend")
        lines.append("")
        for w in macrocycle.weeks:
            marker = " [D]" if w.is_deload_week else ""
            bar = "█" * min(40, w.total_sets)
            lines.append(f"  Week {w.week_number:2d}{marker}: {bar} {w.total_sets}")
        return "\n".join(lines)

    @staticmethod
    def generate_metrics_report(metrics: PlanningMetrics) -> str:
        lines: list[str] = []
        lines.append("# Planning Metrics Report")
        lines.append("")
        lines.append("## Overview")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Total Plans | {metrics.total_plans} |")
        lines.append(f"| Active Plans | {metrics.active_plans} |")
        lines.append(f"| Completed Plans | {metrics.completed_plans} |")
        lines.append("")
        lines.append("## Average Quality Scores")
        lines.append("")
        lines.append("| Metric | Score |")
        lines.append("|--------|-------|")
        lines.append(f"| Plan Quality | {metrics.avg_plan_quality:.0%} |")
        lines.append(f"| Scientific Score | {metrics.avg_scientific_score:.0%} |")
        lines.append(f"| Recovery Balance | {metrics.avg_recovery_balance:.0%} |")
        lines.append(f"| Fatigue Balance | {metrics.avg_fatigue_balance:.0%} |")
        lines.append(f"| Specificity | {metrics.avg_specificity:.0%} |")
        lines.append(f"| Adherence Prediction | {metrics.avg_adherence_prediction:.0%} |")
        lines.append("")
        lines.append("## Content Summary")
        lines.append("")
        lines.append("| Metric | Count |")
        lines.append("|--------|-------|")
        lines.append(f"| Total Mesocycles | {metrics.total_mesocycles} |")
        lines.append(f"| Total Sessions | {metrics.total_sessions} |")
        lines.append(f"| Total Sets | {metrics.total_sets} |")
        lines.append(f"| Validation Errors | {metrics.total_validation_errors} |")
        lines.append(f"| Validation Warnings | {metrics.total_validation_warnings} |")
        return "\n".join(lines)

    @staticmethod
    def generate_comparison_report(plans: list[Macrocycle], validator: PlanningValidator) -> str:
        if not plans:
            return "No plans to compare."
        scorer = PlanningMetricsScorer()
        lines: list[str] = []
        lines.append("# Plan Comparison Report")
        lines.append("")
        lines.append("| Plan | Weeks | Sessions | Sets | Quality | Scientific | Recovery | Adherence |")
        lines.append("|------|-------|----------|------|---------|------------|----------|-----------|")
        for plan in plans:
            quality = scorer.score_plan_quality(plan)
            lines.append(
                f"| {plan.name} | {plan.total_weeks} | {plan.total_sessions} | "
                f"{plan.total_sets} | {quality.overall:.0%} | {quality.scientific_score:.0%} | "
                f"{quality.recovery_balance:.0%} | {quality.adherence_prediction:.0%} |"
            )
        return "\n".join(lines)

    @staticmethod
    def generate_weekly_overview(macrocycle: Macrocycle, week_number: int) -> str:
        week = next((w for w in macrocycle.weeks if w.week_number == week_number), None)
        if week is None:
            return f"Week {week_number} not found in macrocycle."
        lines: list[str] = []
        lines.append(f"# Week {week_number} Overview")
        lines.append("")
        if week.is_deload_week:
            lines.append("**⚠ DELOAD WEEK** — Reduce load 40-50%")
            lines.append("")
        lines.append(f"**Sessions:** {week.session_count}")
        lines.append(f"**Total Sets:** {week.total_sets}")
        lines.append(f"**Total Duration:** {week.total_training_duration_minutes}m")
        lines.append("")
        if week.recovery_budget:
            lines.append(f"**Recovery Capacity:** {week.recovery_budget.recovery_capacity:.0%}")
        lines.append("")
        lines.append("## Daily Schedule")
        lines.append("")
        for session in week.sessions:
            icon = "📅" if session.day_type.value == "rest" else "🏋️"
            duration = f" ({session.estimated_duration_minutes}m)" if session.estimated_duration_minutes > 0 else ""
            label = session.day_type.label
            sets_info = f", {session.total_sets} sets" if session.total_sets > 0 else ""
            lines.append(f"  {icon} Day {session.day_of_week + 1}: {label}{duration}{sets_info}")
        return "\n".join(lines)
