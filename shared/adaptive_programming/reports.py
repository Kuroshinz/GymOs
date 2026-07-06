"""Adaptive Programming Reports — Human-readable reports for adaptive plans."""

from __future__ import annotations

from datetime import datetime

from shared.adaptive_programming.domain import (
    AdaptiveMetrics,
    AdaptivePlan,
    DecisionStatus,
)
from shared.adaptive_programming.metrics import AdaptiveMetricsCalculator


class AdaptiveReportGenerator:
    """Generates formatted text reports for adaptive programming data."""

    def __init__(self) -> None:
        self._metrics = AdaptiveMetricsCalculator()

    def generate_adaptive_report(
        self,
        plan: AdaptivePlan,
        metrics: AdaptiveMetrics,
    ) -> str:
        """Comprehensive adaptive plan report covering all dimensions."""
        lines: list[str] = []
        lines.append("=== Adaptive Programming Report ===")
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append(f"Plan ID  : {plan.plan_id}")
        lines.append(f"User ID  : {plan.user_id}")
        lines.append("")

        lines.append("--- Strategy Overview ---")
        lines.append(f"Phase            : {plan.strategy.phase.label}")
        lines.append(f"Goal             : {plan.strategy.goal}")
        lines.append(f"Base Volume      : {plan.strategy.base_volume}")
        lines.append(f"Current Volume   : {plan.strategy.current_volume}")
        lines.append(f"Volume Delta     : {plan.strategy.volume_delta}")
        lines.append(f"Base Frequency   : {plan.strategy.base_frequency}")
        lines.append(f"Current Frequency: {plan.strategy.current_frequency}")
        lines.append(f"Frequency Delta  : {plan.strategy.frequency_delta}")
        lines.append("")

        lines.append("--- Decision Summary ---")
        lines.append(f"Total Decisions     : {plan.decision_count}")
        lines.append(f"Active Decisions    : {plan.active_decision_count}")
        lines.append(f"Rolled Back         : {plan.rollback_count}")
        lines.append("")

        lines.append("--- Metrics ---")
        lines.append(f"Total Adaptations   : {metrics.total_adaptations}")
        lines.append(f"Approved            : {metrics.approved_adaptations}")
        lines.append(f"Rejected            : {metrics.rejected_adaptations}")
        lines.append(f"Rolled Back         : {metrics.rolled_back_adaptations}")
        lines.append(f"Adaptation Frequency: {metrics.adaptation_frequency:.4f}")
        lines.append(f"Adaptation Quality  : {metrics.adaptation_quality:.4f}")
        lines.append(f"Success Rate        : {metrics.success_rate:.4f}")
        lines.append(f"Rollback Rate       : {metrics.rollback_rate:.4f}")
        lines.append(f"Strategy Stability  : {metrics.strategy_stability:.4f}")
        lines.append("")

        lines.append("--- History ---")
        lines.append(f"Total History Records: {len(plan.history)}")
        if plan.history:
            lines.append("Recent events:")
            for h in sorted(plan.history, key=lambda x: x.adapted_at, reverse=True)[:5]:
                lines.append(
                    f"  {h.history_id}: {h.adaptation_type.label} "
                    f"({h.previous_value} -> {h.new_value}) "
                    f"[{h.status.label}] score={h.outcome_score}"
                )
        lines.append("")

        return "\n".join(lines)

    def generate_strategy_evolution(
        self,
        plan: AdaptivePlan,
    ) -> str:
        """Strategy evolution over time."""
        lines: list[str] = []
        lines.append("=== Strategy Evolution ===")
        lines.append(f"Plan ID: {plan.plan_id}")
        lines.append(f"User ID: {plan.user_id}")
        lines.append("")

        lines.append("--- Current Strategy ---")
        lines.append(f"Phase       : {plan.strategy.phase.label}")
        lines.append(f"Volume      : {plan.strategy.base_volume} -> {plan.strategy.current_volume}")
        lines.append(f"Frequency   : {plan.strategy.base_frequency} -> {plan.strategy.current_frequency}")
        lines.append("")

        lines.append("--- Evolution Steps ---")
        if not plan.decisions:
            lines.append("No adaptations recorded.")
        else:
            sorted_decisions = sorted(
                plan.decisions, key=lambda d: d.applied_at
            )
            for idx, d in enumerate(sorted_decisions, start=1):
                status_icon = {
                    DecisionStatus.APPROVED: "[+]",
                    DecisionStatus.REJECTED: "[-]",
                    DecisionStatus.ROLLED_BACK: "[x]",
                    DecisionStatus.PENDING: "[?]",
                    DecisionStatus.COMPLETED: "[ok]",
                }.get(d.status, "[ ]")
                lines.append(
                    f"  {idx:>3}. {status_icon} {d.adaptation_type.label:<25} "
                    f"{d.previous_value:>8} -> {d.new_value:<8} "
                    f"({d.applied_at})"
                )
        lines.append("")

        return "\n".join(lines)

    def generate_adaptation_history(
        self,
        plan: AdaptivePlan,
    ) -> str:
        """Chronological adaptation history list."""
        lines: list[str] = []
        lines.append("=== Adaptation History ===")
        lines.append(f"Plan ID: {plan.plan_id}")
        lines.append(f"Total Entries: {len(plan.history)}")
        lines.append("")

        if not plan.history:
            lines.append("No history entries found.")
        else:
            sorted_history = sorted(
                plan.history, key=lambda h: h.adapted_at, reverse=True
            )
            header = (
                f"{'ID':<40} {'Type':<22} {'Prev':>8} {'New':<8} "
                f"{'Score':>6} {'Status':<14} {'Date':<22}"
            )
            lines.append(header)
            lines.append("-" * len(header))
            for h in sorted_history:
                lines.append(
                    f"{h.history_id:<40} {h.adaptation_type.label:<22} "
                    f"{h.previous_value:>8} {h.new_value:<8} "
                    f"{h.outcome_score:>6.2f} {h.status.label:<14} "
                    f"{h.adapted_at:<22}"
                )
        lines.append("")

        return "\n".join(lines)
