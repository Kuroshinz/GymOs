"""Kernel Reports — generates reports in multiple formats.

Stateless formatting functions. No file I/O.
"""

from __future__ import annotations

from typing import Any

from shared.kernel.kernel import (
    KernelRuntime,
    KernelSnapshot,
    ProductHealth,
    ReleaseReadinessResult,
    RuntimeMetrics,
)
from shared.kernel.kernel_history import compute_all_trends, compute_timeline
from shared.kernel.kernel_metrics import AggregatedMetrics


def generate_markdown_report(
    runtime: KernelRuntime,
    metrics: list[RuntimeMetrics],
    health: ProductHealth,
    release: ReleaseReadinessResult,
    aggregated: AggregatedMetrics,
    snapshots: list[KernelSnapshot] | None = None,
) -> str:
    """Generate a full Markdown kernel report."""
    lines: list[str] = []
    lines.append("# GymOS Kernel Report")
    lines.append("")
    lines.append(f"**Version:** {runtime.version}")
    lines.append(f"**Phase:** {runtime.phase.name} / {runtime.roadmap_stage.name}")
    lines.append(f"**Milestone:** {runtime.current_rfc}")
    lines.append(f"**Next:** {runtime.next_rfc}")
    lines.append("")

    # Product Health
    lines.append("## Product Health")
    lines.append("")
    lines.append("| Dimension | Score |")
    lines.append("|-----------|-------|")
    lines.append(f"| Overall | {health.overall}/100 |")
    lines.append(f"| Architecture | {health.architecture_health}/100 |")
    lines.append(f"| Engineering | {health.engineering_health}/100 |")
    lines.append(f"| Knowledge | {health.knowledge_health}/100 |")
    lines.append(f"| Capability | {health.capability_health}/100 |")
    lines.append(f"| Documentation | {health.documentation_health}/100 |")
    lines.append("")

    # Platform Summary
    lines.append("## Platform Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total Capabilities | {runtime.total_capabilities} |")
    lines.append(f"| Complete | {runtime.capabilities_complete} |")
    lines.append(f"| In Progress | {runtime.capabilities_in_progress} |")
    lines.append(f"| Not Started | {runtime.capabilities_not_started} |")
    lines.append(f"| Blocked | {runtime.capabilities_blocked} |")
    lines.append(f"| Total Debt | {runtime.total_technical_debt} |")
    lines.append(f"| Blocking Debt | {runtime.blocking_debt} |")
    lines.append(f"| Weakest | {runtime.weakest_capability} |")
    lines.append(f"| Strongest | {runtime.strongest_capability} |")
    lines.append("")

    # Runtime Capability Matrix
    lines.append("## Capability Runtime Matrix")
    lines.append("")
    lines.append("| Capability | Runtime Maturity | Architecture | Documentation | Tests | Completion | Debt | Dep Health |")
    lines.append("|------------|-----------------|--------------|---------------|-------|------------|------|------------|")
    for m in sorted(metrics, key=lambda x: x.runtime_maturity, reverse=True):
        lines.append(
            f"| {m.name} "
            f"| {m.runtime_maturity} "
            f"| {m.architecture_score} "
            f"| {m.documentation_score} "
            f"| {m.test_score} "
            f"| {m.coverage_score} "
            f"| {m.debt_score} "
            f"| {m.dependency_health} |"
        )
    lines.append("")

    # Aggregated Metrics
    lines.append("## Aggregated Platform Metrics")
    lines.append("")
    lines.append("| Metric | Average |")
    lines.append("|--------|---------|")
    lines.append(f"| Runtime Maturity | {aggregated.avg_runtime_maturity} |")
    lines.append(f"| Architecture | {aggregated.avg_architecture} |")
    lines.append(f"| Documentation | {aggregated.avg_documentation} |")
    lines.append(f"| Test Coverage | {aggregated.avg_test_coverage} |")
    lines.append(f"| Completion | {aggregated.avg_completion} |")
    lines.append(f"| Debt Score | {aggregated.avg_debt_score} |")
    lines.append(f"| Dependency Health | {aggregated.avg_dependency_health} |")
    lines.append("")

    # Release Readiness
    lines.append("## Release Readiness")
    lines.append("")
    lines.append(f"**Target:** v{release.version}")
    lines.append(f"**Score:** {release.score}/100")
    lines.append(f"**Readiness:** {release.readiness.name.replace('_', ' ')}")
    lines.append("")
    if release.blockers:
        lines.append("### Blockers")
        for b in release.blockers:
            lines.append(f"- {b}")
        lines.append("")
    if release.gaps:
        lines.append("### Gaps")
        for g in release.gaps:
            lines.append(f"- {g}")
        lines.append("")

    # Timeline
    if snapshots:
        lines.append("## Snapshot Timeline")
        lines.append("")
        timeline = compute_timeline(snapshots)
        for entry in timeline:
            lines.append(f"- **{entry['timestamp']}** ({entry['type']}): Health {entry['overall_health']:.1f}, "
                         f"{entry['complete']}/{entry['total_capabilities']} complete")
        lines.append("")

    return "\n".join(lines)


def generate_json_report(
    runtime: KernelRuntime,
    metrics: list[RuntimeMetrics],
    health: ProductHealth,
    release: ReleaseReadinessResult,
    aggregated: AggregatedMetrics,
    debt_items: list | None = None,
    snapshots: list[KernelSnapshot] | None = None,
) -> dict[str, Any]:
    """Generate a JSON-serializable kernel report."""
    report: dict[str, Any] = {
        "kernel": {
            "version": runtime.version,
            "phase": runtime.phase.name,
            "roadmap_stage": runtime.roadmap_stage.name,
            "current_rfc": runtime.current_rfc,
            "next_rfc": runtime.next_rfc,
        },
        "health": {
            "overall": health.overall,
            "architecture": health.architecture_health,
            "engineering": health.engineering_health,
            "knowledge": health.knowledge_health,
            "capability": health.capability_health,
            "documentation": health.documentation_health,
        },
        "platform": {
            "total_capabilities": runtime.total_capabilities,
            "complete": runtime.capabilities_complete,
            "in_progress": runtime.capabilities_in_progress,
            "not_started": runtime.capabilities_not_started,
            "blocked": runtime.capabilities_blocked,
            "total_debt": runtime.total_technical_debt,
            "blocking_debt": runtime.blocking_debt,
            "weakest": runtime.weakest_capability,
            "strongest": runtime.strongest_capability,
        },
        "aggregated": {
            "avg_runtime_maturity": aggregated.avg_runtime_maturity,
            "avg_architecture": aggregated.avg_architecture,
            "avg_documentation": aggregated.avg_documentation,
            "avg_test_coverage": aggregated.avg_test_coverage,
            "avg_completion": aggregated.avg_completion,
            "avg_debt_score": aggregated.avg_debt_score,
            "avg_dependency_health": aggregated.avg_dependency_health,
        },
        "release": {
            "target_version": release.version,
            "score": release.score,
            "readiness": release.readiness.name,
            "blockers": list(release.blockers),
            "gaps": list(release.gaps),
        },
        "capabilities": [
            {
                "id": m.capability_id,
                "name": m.name,
                "runtime_maturity": m.runtime_maturity,
                "architecture": m.architecture_score,
                "documentation": m.documentation_score,
                "tests": m.test_score,
                "completion": m.coverage_score,
                "debt": m.debt_score,
                "dependency_health": m.dependency_health,
            }
            for m in sorted(metrics, key=lambda x: x.runtime_maturity, reverse=True)
        ],
    }

    if snapshots:
        report["timeline"] = compute_timeline(snapshots)

    return report


def generate_console_summary(
    runtime: KernelRuntime,
    health: ProductHealth,
    release: ReleaseReadinessResult,
) -> str:
    """Generate a compact console-friendly summary."""
    lines: list[str] = []
    lines.append(f"GymOS {runtime.version} — {runtime.phase.name} / {runtime.roadmap_stage.name}")
    lines.append(f"Health: {health.overall}/100")
    lines.append(f"Capabilities: {runtime.capabilities_complete}/{runtime.total_capabilities} complete")
    lines.append(f"RFC: {runtime.current_rfc} -> {runtime.next_rfc}")
    lines.append(f"Release Readiness: {release.readiness.name.replace('_', ' ')} ({release.score}/100)")
    if release.blockers:
        lines.append(f"Blockers: {release.blocker_count}")
    return "\n".join(lines)


def generate_capability_timeline_report(snapshots: list[KernelSnapshot]) -> str:
    """Generate a capability evolution report from snapshots."""
    from shared.kernel.kernel_history import compute_platform_trend

    lines: list[str] = []
    lines.append("# Capability Timeline Report")
    lines.append("")

    if not snapshots:
        lines.append("No snapshots recorded.")
        return "\n".join(lines)

    lines.append(f"**Snapshots:** {len(snapshots)}")
    lines.append("")

    # Platform trend
    platform_trend = compute_platform_trend(snapshots)
    lines.append(f"**Platform Trend:** {platform_trend.growth_rate:+.1f}%")
    lines.append("")

    # Per-capability trends
    trends = compute_all_trends(snapshots)
    lines.append("## Capability Trends")
    lines.append("")
    lines.append("| Capability | Growth Rate | Points | First | Last |")
    lines.append("|------------|-------------|--------|-------|------|")
    for t in sorted(trends, key=lambda x: x.growth_rate, reverse=True):
        if t.points:
            first_val = t.points[0].value
            last_val = t.points[-1].value
            lines.append(f"| {t.name} | {t.growth_rate:+.1f}% | {len(t.points)} | {first_val} | {last_val} |")
    lines.append("")

    return "\n".join(lines)


def generate_debt_summary(debt_items: list) -> str:
    """Generate a technical debt summary."""
    lines: list[str] = []
    lines.append("# Technical Debt Summary")
    lines.append("")

    if not debt_items:
        lines.append("No debt items registered.")
        return "\n".join(lines)

    # Group by capability
    by_cap: dict[str, list] = {}
    for item in debt_items:
        cap = getattr(item, "affected_capability", "unknown")
        if cap not in by_cap:
            by_cap[cap] = []
        by_cap[cap].append(item)

    for cap in sorted(by_cap):
        items = by_cap[cap]
        blocking = sum(1 for i in items if getattr(i, "blocking", False))
        lines.append(f"### {cap} ({len(items)} items, {blocking} blocking)")
        lines.append("")
        lines.append("| ID | Title | Severity | Status | Blocking |")
        lines.append("|----|-------|----------|--------|----------|")
        for item in items:
            lines.append(f"| {getattr(item, 'debt_id', '?')} | {getattr(item, 'title', '?')} | "
                         f"{getattr(item, 'severity', '?')} | {getattr(item, 'status', '?')} | "
                         f"{'Yes' if getattr(item, 'blocking', False) else 'No'} |")
        lines.append("")

    return "\n".join(lines)


def generate_product_summary(
    runtime: KernelRuntime,
    health: ProductHealth,
    release: ReleaseReadinessResult,
    aggregated: AggregatedMetrics,
) -> str:
    """Generate a one-page product summary."""
    lines: list[str] = []
    lines.append(f"# GymOS Product Summary — v{runtime.version}")
    lines.append("")
    lines.append(f"**Phase:** {runtime.phase.name} / {runtime.roadmap_stage.name}")
    lines.append(f"**Current RFC:** {runtime.current_rfc} -> **Next:** {runtime.next_rfc}")
    lines.append(f"**Health:** {health.overall}/100")
    lines.append(f"**Capabilities:** {runtime.capabilities_complete}/{runtime.total_capabilities} complete")
    lines.append(f"**Release Readiness:** {release.readiness.name.replace('_', ' ')} ({release.score}/100)")
    lines.append(f"**Technical Debt:** {runtime.total_technical_debt} items ({runtime.blocking_debt} blocking)")
    lines.append(f"**Weakest:** {runtime.weakest_capability}")
    lines.append(f"**Strongest:** {runtime.strongest_capability}")
    lines.append("")
    lines.append("### Health Dimensions")
    lines.append(f"- Architecture: {health.architecture_health}/100")
    lines.append(f"- Engineering: {health.engineering_health}/100")
    lines.append(f"- Knowledge: {health.knowledge_health}/100")
    lines.append(f"- Capability: {health.capability_health}/100")
    lines.append(f"- Documentation: {health.documentation_health}/100")
    lines.append("")
    return "\n".join(lines)
