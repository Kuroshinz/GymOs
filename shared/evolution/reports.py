"""Reports — generates evolution reports in multiple formats.

Stateless formatting functions. No file I/O.
"""

from __future__ import annotations

from typing import Any

from shared.evolution.evolution_engine import (
    CapabilityVelocity,
    EstimatedRemainingWork,
    EvolutionChain,
    EvolutionSummary,
    EvolutionTimeline,
    EvolutionVelocity,
    ProductCompletion,
    ProductCompletionForecast,
    RfcContribution,
    RfcImpactScore,
    VersionReadinessTrend,
)
from shared.evolution.milestone_graph import MilestoneProgress


def generate_evolution_report(
    completion: ProductCompletion,
    velocities: list[CapabilityVelocity],
    rfc_impacts: list[RfcImpactScore],
    version_trends: list[VersionReadinessTrend],
    timeline: EvolutionTimeline,
    forecast: ProductCompletionForecast,
    remaining: EstimatedRemainingWork,
    milestones: list[MilestoneProgress],
) -> str:
    """Generate a complete Markdown evolution report."""
    lines: list[str] = []
    lines.append("# GymOS Evolution Report")
    lines.append("")

    # Product Completion
    lines.append("## Product Completion")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Capabilities | {completion.total_capabilities} |")
    lines.append(f"| Complete | {completion.complete} |")
    lines.append(f"| In Progress | {completion.in_progress} |")
    lines.append(f"| Not Started | {completion.not_started} |")
    lines.append(f"| Completion % | {completion.completion_percent}% |")
    lines.append(f"| Est. Remaining Sprints | {remaining.estimated_sprints} |")
    lines.append(f"| Est. Remaining Weeks | {remaining.estimated_weeks} |")
    lines.append("")

    # Milestone Progress
    lines.append("## Milestone Progress")
    lines.append("")
    lines.append("| Milestone | Version | Progress | Status |")
    lines.append("|-----------|---------|----------|--------|")
    for m in milestones:
        status = "Reached" if m.is_reached else "In Progress"
        lines.append(f"| {m.label} | v{m.target_version} | {m.completion_percent}% | {status} |")
    lines.append("")

    # Capability Velocities
    if velocities:
        lines.append("## Capability Velocity")
        lines.append("")
        lines.append("| Capability | Velocity | Maturity Gain | Growth Rate |")
        lines.append("|------------|----------|---------------|-------------|")
        for v in sorted(velocities, key=lambda x: x.velocity, reverse=True):
            lines.append(f"| {v.name} | {v.velocity} | {v.maturity_gain} | {v.growth_rate:+.1f}% |")
        lines.append("")

        fastest = max(velocities, key=lambda x: x.velocity)
        slowest = min(velocities, key=lambda x: x.velocity)
        lines.append(f"**Fastest:** {fastest.name} ({fastest.velocity})")
        lines.append(f"**Slowest:** {slowest.name} ({slowest.velocity})")
        lines.append("")

    # RFC Impact
    if rfc_impacts:
        lines.append("## RFC Impact Scores")
        lines.append("")
        lines.append("| RFC | Title | Impact Score | Capabilities | Maturity Gain |")
        lines.append("|-----|-------|--------------|--------------|---------------|")
        for rfc in rfc_impacts:
            lines.append(f"| {rfc.rfc_id} | {rfc.title} | {rfc.impact_score} | {rfc.capabilities_affected} | {rfc.maturity_gain} |")
        lines.append("")

        if rfc_impacts:
            lines.append(f"**Most Impactful:** {rfc_impacts[0].rfc_id} ({rfc_impacts[0].title})")
            lines.append("")

    # RFC Contributions
    contributions = _build_contributions_for_report()
    if contributions:
        lines.append("## RFC Contributions to Evolution")
        lines.append("")
        lines.append("| RFC | Status | Contribution % | Capabilities | Maturity |")
        lines.append("|-----|--------|----------------|--------------|----------|")
        for c in sorted(contributions, key=lambda x: x.contribution_percent, reverse=True):
            lines.append(f"| {c.rfc_id} | {c.status} | {c.contribution_percent}% | {c.capabilities_affected} | {c.maturity_contribution} |")
        lines.append("")

    # Evolution Velocity
    velocity = _build_velocity_for_report()
    lines.append("## Evolution Velocity")
    lines.append("")
    lines.append(f"**Velocity Score:** {velocity.velocity_score}")
    lines.append(f"**Maturity Delta:** {velocity.maturity_delta}")
    lines.append(f"**Capabilities Completed:** {velocity.capabilities_completed}")
    lines.append("")

    # Version Readiness Trend
    if version_trends:
        lines.append("## Version Readiness Trend")
        lines.append("")
        lines.append("| Version | Readiness Score | Trend | Delta |")
        lines.append("|---------|-----------------|-------|-------|")
        for t in version_trends:
            lines.append(f"| v{t.version} | {t.readiness_score}/100 | {t.trend_direction} | {t.delta:+.1f} |")
        lines.append("")

    # Forecast
    lines.append("## Product Completion Forecast")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Current Completion | {forecast.current_completion}% |")
    lines.append(f"| Predicted After Next RFC | {forecast.predicted_completion_next_rfc}% |")
    lines.append(f"| Predicted at v1.0 | {forecast.predicted_completion_v1}% |")
    lines.append(f"| Estimated Sprints to v1.0 | {forecast.sprints_to_v1} |")
    lines.append(f"| Estimated Health at v1.0 | {forecast.estimated_health_at_v1}/100 |")
    lines.append(f"| Confidence | {forecast.confidence} |")
    lines.append("")

    # Evolution Chain (RFC → Capability → Milestone → Version)
    lines.append("## Evolution Chain")
    lines.append("")
    lines.append("| RFC | Capability | Milestone | Version |")
    lines.append("|-----|------------|-----------|---------|")
    chain = _build_chain_for_report()
    for link in chain.links[:12]:
        lines.append(f"| {link.rfc_id}: {link.rfc_title} | {link.capability_name} | {link.milestone_label} | v{link.milestone_version} |")
    if len(chain.links) > 12:
        lines.append(f"| ... and {len(chain.links) - 12} more links | | | |")
    lines.append("")

    # Timeline summary
    lines.append("## Evolution Timeline")
    lines.append("")
    lines.append(f"**Events:** {len(timeline.entries)}")
    if timeline.entries:
        lines.append("")
        lines.append("| Date | Type | Event |")
        lines.append("|------|------|-------|")
        for entry in timeline.entries[:20]:  # show first 20
            lines.append(f"| {entry.timestamp} | {entry.event_type} | {entry.label} |")
    lines.append("")

    return "\n".join(lines)


def _build_chain_for_report() -> EvolutionChain:
    """Build evolution chain for report generation."""
    from shared.evolution.timeline import build_evolution_chain
    return build_evolution_chain()


def _build_velocity_for_report() -> EvolutionVelocity:
    """Build evolution velocity for report generation."""
    from shared.evolution.capability_history import compute_evolution_velocity
    return compute_evolution_velocity()


def _build_contributions_for_report() -> list[RfcContribution]:
    """Build RFC contributions for report generation."""
    from shared.evolution.capability_history import compute_rfc_contributions
    return compute_rfc_contributions()


def generate_evolution_summary_report(summary: EvolutionSummary) -> str:
    """Generate a concise evolution summary report."""
    lines: list[str] = []
    lines.append("# GymOS Evolution Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total RFCs | {summary.total_rfcs} |")
    lines.append(f"| Completed RFCs | {summary.completed_rfcs} |")
    lines.append(f"| Total Capabilities | {summary.total_capabilities} |")
    lines.append(f"| Completed Capabilities | {summary.completed_capabilities} |")
    lines.append(f"| Total Milestones | {summary.total_milestones} |")
    lines.append(f"| Reached Milestones | {summary.reached_milestones} |")
    lines.append(f"| Total Versions | {summary.total_versions} |")
    lines.append(f"| Released Versions | {summary.released_versions} |")
    lines.append(f"| Overall Evolution Progress | {summary.overall_evolution_progress}% |")
    lines.append(f"| Evolution Velocity | {summary.evolution_velocity.velocity_score} |")
    lines.append(f"| Fastest Capability | {summary.fastest_capability} |")
    lines.append(f"| Slowest Capability | {summary.slowest_capability} |")
    lines.append(f"| Most Impactful RFC | {summary.most_impactful_rfc} |")
    lines.append("")
    return "\n".join(lines)


def generate_json_evolution_report(
    completion: ProductCompletion,
    velocities: list[CapabilityVelocity],
    rfc_impacts: list[RfcImpactScore],
    version_trends: list[VersionReadinessTrend],
    forecast: ProductCompletionForecast,
    remaining: EstimatedRemainingWork,
    milestones: list[MilestoneProgress],
) -> dict[str, Any]:
    """Generate a JSON-serializable evolution report."""
    return {
        "product_completion": {
            "total_capabilities": completion.total_capabilities,
            "complete": completion.complete,
            "in_progress": completion.in_progress,
            "not_started": completion.not_started,
            "completion_percent": completion.completion_percent,
            "estimated_remaining_sprints": remaining.estimated_sprints,
            "estimated_remaining_weeks": remaining.estimated_weeks,
        },
        "milestones": [
            {
                "label": m.label,
                "version": m.target_version,
                "completion_percent": m.completion_percent,
                "is_reached": m.is_reached,
            }
            for m in milestones
        ],
        "capability_velocities": [
            {
                "name": v.name,
                "velocity": v.velocity,
                "maturity_gain": v.maturity_gain,
                "growth_rate": v.growth_rate,
            }
            for v in sorted(velocities, key=lambda x: x.velocity, reverse=True)
        ],
        "rfc_impacts": [
            {
                "rfc_id": r.rfc_id,
                "title": r.title,
                "impact_score": r.impact_score,
                "capabilities_affected": r.capabilities_affected,
                "maturity_gain": r.maturity_gain,
            }
            for r in rfc_impacts
        ],
        "version_readiness_trends": [
            {
                "version": t.version,
                "readiness_score": t.readiness_score,
                "trend_direction": t.trend_direction,
                "delta": t.delta,
            }
            for t in version_trends
        ],
        "evolution_chain": [
            {
                "rfc_id": link.rfc_id,
                "rfc_title": link.rfc_title,
                "capability": link.capability_name,
                "milestone": link.milestone_label,
                "version": link.milestone_version,
            }
            for link in _build_chain_for_report().links
        ],
        "rfc_contributions": [
            {
                "rfc_id": c.rfc_id,
                "status": c.status,
                "contribution_percent": c.contribution_percent,
                "capabilities_affected": c.capabilities_affected,
                "maturity_contribution": c.maturity_contribution,
            }
            for c in _build_contributions_for_report()
        ],
        "evolution_velocity": (lambda _v: {
            "velocity_score": _v.velocity_score,
            "maturity_delta": _v.maturity_delta,
            "capabilities_completed": _v.capabilities_completed,
        })(_build_velocity_for_report()),
        "forecast": {
            "current_completion": forecast.current_completion,
            "predicted_next_rfc": forecast.predicted_completion_next_rfc,
            "predicted_v1": forecast.predicted_completion_v1,
            "sprints_to_v1": forecast.sprints_to_v1,
            "estimated_health_at_v1": forecast.estimated_health_at_v1,
            "confidence": forecast.confidence,
        },
    }


def generate_version_report(milestones: list[MilestoneProgress]) -> str:
    """Generate a version-by-version progress report."""
    lines: list[str] = []
    lines.append("# Version Progress Report")
    lines.append("")
    lines.append("| Version | Milestone | Progress | Capabilities | Complete | Status |")
    lines.append("|---------|-----------|----------|--------------|----------|--------|")
    for m in milestones:
        status = "Reached" if m.is_reached else "In Progress"
        lines.append(f"| v{m.target_version} | {m.label} | {m.completion_percent}% | {m.capabilities_total} | {m.capabilities_complete} | {status} |")
    lines.append("")
    return "\n".join(lines)


def generate_timeline_report(timeline: EvolutionTimeline) -> str:
    """Generate a timeline report from evolution events."""
    lines: list[str] = []
    lines.append("# Evolution Timeline Report")
    lines.append("")
    lines.append(f"**Total Events:** {len(timeline.entries)}")
    lines.append("")

    if not timeline.entries:
        lines.append("No events recorded.")
        return "\n".join(lines)

    lines.append("| Date | Type | Event | Details |")
    lines.append("|------|------|-------|---------|")
    for entry in timeline.entries:
        lines.append(f"| {entry.timestamp} | {entry.event_type} | {entry.label} | {entry.description} |")
    lines.append("")

    return "\n".join(lines)


def generate_forecast_report(
    forecast: ProductCompletionForecast,
    remaining: EstimatedRemainingWork,
    milestones: list[MilestoneProgress],
) -> str:
    """Generate a product forecast report."""
    lines: list[str] = []
    lines.append("# Product Forecast Report")
    lines.append("")

    # Current state
    next_milestone = milestones[0] if milestones else None
    for m in milestones:
        if not m.is_reached:
            next_milestone = m
            break

    lines.append("## Current State")
    lines.append("")
    lines.append(f"**Completion:** {forecast.current_completion}%")
    if next_milestone:
        lines.append(f"**Next Milestone:** {next_milestone.label} (v{next_milestone.target_version})")
        lines.append(f"**Milestone Progress:** {next_milestone.completion_percent}%")
    lines.append("")

    # Forecast
    lines.append("## Forecast")
    lines.append("")
    lines.append("| Metric | Value | Confidence |")
    lines.append("|--------|-------|------------|")
    lines.append(f"| Completion after next RFC | {forecast.predicted_completion_next_rfc}% | medium |")
    lines.append(f"| Completion at v1.0 | {forecast.predicted_completion_v1}% | {forecast.confidence} |")
    lines.append(f"| Sprints to v1.0 | {forecast.sprints_to_v1} | {forecast.confidence} |")
    lines.append(f"| Health at v1.0 | {forecast.estimated_health_at_v1}/100 | {forecast.confidence} |")
    lines.append(f"| Remaining Capabilities | {remaining.remaining} | {remaining.confidence} |")
    lines.append(f"| Est. Work to v1.0 | {remaining.estimated_weeks} weeks ({remaining.estimated_sprints} sprints) | {remaining.confidence} |")
    lines.append("")

    return "\n".join(lines)


def generate_product_journey(milestones: list[MilestoneProgress]) -> str:
    """Generate a product journey report — the full evolution story."""
    lines: list[str] = []
    lines.append("# Product Journey")
    lines.append("")
    lines.append("The evolution of GymOS from concept to Personal Hypertrophy Operating System.")
    lines.append("")

    for i, m in enumerate(milestones):
        status_icon = "Reached" if m.is_reached else "In Progress"
        lines.append(f"## Milestone {i+1}: {m.label} (v{m.target_version})")
        lines.append("")
        lines.append(f"**Status:** {status_icon}")
        lines.append(f"**Progress:** {m.completion_percent}%")
        lines.append(f"**Description:** {m.description}")
        lines.append("")
        lines.append(f"| {'Capabilities'}: | {'Complete'}: {m.capabilities_complete}/{m.capabilities_total} |")
        lines.append("")

    # Final destination
    lines.append("---")
    lines.append("## Destination: v1.0 — Personal Hypertrophy Operating System")
    lines.append("")
    lines.append("When all milestones are reached, GymOS becomes a fully autonomous")
    lines.append("training companion that plans, executes, analyzes, and adapts")
    lines.append("workouts, nutrition, and recovery without manual intervention.")
    lines.append("")

    return "\n".join(lines)
