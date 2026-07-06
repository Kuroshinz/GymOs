"""Report Generator — produces capability reports in multiple formats.

Stateless formatting functions. No file I/O — returns strings and dicts.
"""

from __future__ import annotations

from shared.capabilities.dependency_graph import build_dependency_graph
from shared.capabilities.platform_state import compute_platform_state
from shared.capabilities.registry import CapabilityRegistry


def generate_markdown_report(registry: CapabilityRegistry) -> str:
    """Generate a full Markdown capability report."""
    state = compute_platform_state(registry)
    dep_graph = build_dependency_graph(registry)

    lines: list[str] = []
    lines.append("# GymOS Capability Report")
    lines.append("")
    lines.append(f"**Version:** {state.current_version}")
    lines.append(f"**Milestone:** {state.current_milestone}")
    lines.append(f"**Overall Health:** {state.overall_health}/100")
    lines.append("")

    # Summary table
    lines.append("## Platform Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Capabilities | {state.total_capabilities} |")
    lines.append(f"| Complete | {state.capabilities_complete} |")
    lines.append(f"| In Progress | {state.capabilities_in_progress} |")
    lines.append(f"| Not Started | {state.capabilities_not_started} |")
    lines.append(f"| Blocked | {state.capabilities_blocked} |")
    lines.append(f"| Total Technical Debt | {state.total_technical_debt} |")
    lines.append(f"| Blocking Debt Items | {state.blocking_debt} |")
    lines.append(f"| Weakest Capability | {state.weakest_capability} |")
    lines.append(f"| Strongest Capability | {state.strongest_capability} |")
    lines.append("")

    # Capability matrix
    lines.append("## Capability Matrix")
    lines.append("")
    lines.append("| Capability | Current | Target | Status | Health | Completion |")
    lines.append("|------------|---------|--------|--------|--------|------------|")
    for cap in registry.list_all():
        lines.append(
            f"| {cap.name} "
            f"| {cap.current_maturity.name} "
            f"| {cap.target_maturity.name} "
            f"| {cap.status.name} "
            f"| {cap.health.overall}/100 "
            f"| {cap.completion.current_percent:.0f}% |"
        )
    lines.append("")

    # Gap analysis
    if state.gaps:
        lines.append("## Maturity Gaps")
        lines.append("")
        lines.append("| Capability | Current | Target | Gap | Health | Blocked |")
        lines.append("|------------|---------|--------|-----|--------|---------|")
        for gap in state.gaps:
            if gap.maturity_gap > 0:
                lines.append(
                    f"| {gap.name} "
                    f"| {gap.current_maturity.name} "
                    f"| {gap.target_maturity.name} "
                    f"| {gap.maturity_gap} levels "
                    f"| {gap.health_score}/100 "
                    f"| {'Yes' if gap.is_blocked else 'No'} |"
                )
        lines.append("")

    # Dependency graph
    if dep_graph.levels:
        lines.append("## Dependency Graph")
        lines.append("")
        for i, level in enumerate(dep_graph.levels):
            lines.append(f"**Level {i}:** {', '.join(level)}")
        lines.append("")

    # Blocking issues
    if state.roadmap.blocking_issues:
        lines.append("## Blocking Issues")
        lines.append("")
        for issue in state.roadmap.blocking_issues:
            lines.append(f"- {issue}")
        lines.append("")

    return "\n".join(lines)


def generate_json_report(registry: CapabilityRegistry) -> dict:
    """Generate a JSON-serializable capability report."""
    state = compute_platform_state(registry)
    caps = registry.list_all()

    return {
        "platform": {
            "version": state.current_version,
            "milestone": state.current_milestone,
            "overall_health": state.overall_health,
            "total_capabilities": state.total_capabilities,
            "complete": state.capabilities_complete,
            "in_progress": state.capabilities_in_progress,
            "not_started": state.capabilities_not_started,
            "blocked": state.capabilities_blocked,
            "total_technical_debt": state.total_technical_debt,
            "blocking_debt": state.blocking_debt,
            "weakest": state.weakest_capability,
            "strongest": state.strongest_capability,
        },
        "capabilities": [
            {
                "id": c.capability_id,
                "name": c.name,
                "category": c.category,
                "current_maturity": c.current_maturity.name,
                "target_maturity": c.target_maturity.name,
                "status": c.status.name,
                "health": c.health.overall,
                "completion": c.completion.current_percent,
                "dependencies": list(c.dependencies),
                "risk_level": c.risk_level.name,
            }
            for c in caps
        ],
    }


def generate_terminal_summary(registry: CapabilityRegistry) -> str:
    """Generate a compact terminal-friendly summary."""
    state = compute_platform_state(registry)

    lines: list[str] = []
    lines.append(f"GymOS {state.current_version} — {state.current_milestone}")
    lines.append(f"Health: {state.overall_health}/100")
    lines.append(f"Capabilities: {state.capabilities_complete}/{state.total_capabilities} complete")
    lines.append(f"Debt: {state.total_technical_debt} items ({state.blocking_debt} blocking)")
    lines.append(f"Weakest: {state.weakest_capability}")
    lines.append(f"Next: {state.roadmap.next_version}")
    if state.roadmap.blocking_issues:
        lines.append(f"Blockers: {len(state.roadmap.blocking_issues)}")
    return "\n".join(lines)
