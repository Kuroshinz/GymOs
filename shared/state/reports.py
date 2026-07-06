"""State Reports — generates Product State Engine reports in Markdown.

Report types:
- Product State Report: current state with all dimensions
- Drift Report: drift analysis across all dimensions
- Confidence Report: confidence scoring assessment
- Runtime Snapshot: complete current snapshot
- Release Confidence Report: release readiness assessment
"""

from __future__ import annotations

from shared.state.confidence import ConfidenceResult
from shared.state.drift import DriftReport
from shared.state.state import ProductState


def generate_state_report(state: ProductState) -> str:
    """Generate a detailed product state report."""
    lines: list[str] = []
    lines.append("# Product State Report")
    lines.append("")
    lines.append(f"**Current State:** {state.label}")
    lines.append(f"**Timestamp:** {state.timestamp}")
    lines.append(f"**Reason:** {state.primary_reason}")
    lines.append("")

    # Health dimensions
    lines.append("## Health")
    lines.append("")
    lines.append("| Dimension | Score |")
    lines.append("|-----------|-------|")
    lines.append(f"| Overall | {state.overall_health}/100 |")
    lines.append(f"| Architecture | {state.architecture_health}/100 |")
    lines.append(f"| Documentation | {state.documentation_health}/100 |")
    lines.append(f"| Test | {state.test_health}/100 |")
    lines.append("")

    # Capabilities
    lines.append("## Capabilities")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total | {state.total_capabilities} |")
    lines.append(f"| Complete | {state.capabilities_complete} |")
    lines.append(f"| In Progress | {state.capabilities_in_progress} |")
    lines.append(f"| Not Started | {state.capabilities_not_started} |")
    lines.append(f"| Blocked | {state.capabilities_blocked} |")
    lines.append(f"| Completion % | {state.completion_percent}% |")
    lines.append("")

    # Risk & Debt
    lines.append("## Risk & Technical Debt")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Risk Score | {state.risk_score}/100 |")
    lines.append(f"| Drift Score | {state.drift_score}/100 |")
    lines.append(f"| Total Technical Debt | {state.technical_debt} items |")
    lines.append(f"| Blocking Debt | {state.blocking_debt} items |")
    lines.append(f"| Debt Pressure | {state.debt_pressure}/100 |")
    lines.append("")

    # Release
    lines.append("## Release Readiness")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Readiness | {state.release_readiness}/100 |")
    lines.append(f"| Momentum | {state.product_momentum:+.1f} |")
    if state.release_blockers:
        lines.append(f"| Blockers ({len(state.release_blockers)}) | {'; '.join(state.release_blockers)} |")
    else:
        lines.append("| Blockers | None |")
    lines.append("")

    # Supporting factors
    if state.supporting_factors:
        lines.append("## Supporting Factors")
        lines.append("")
        for factor in state.supporting_factors:
            lines.append(f"- {factor}")
        lines.append("")

    return "\n".join(lines)


def generate_drift_report(drift: DriftReport) -> str:
    """Generate a drift analysis report."""
    lines: list[str] = []
    lines.append("# Product Drift Report")
    lines.append("")
    lines.append(f"**Overall Drift:** {drift.overall_drift}/100")
    lines.append("")

    lines.append("## Drift Dimensions")
    lines.append("")
    lines.append("| Dimension | Score | Status |")
    lines.append("|-----------|-------|--------|")
    for dim, score in [
        ("Architecture", drift.architecture_drift),
        ("Documentation", drift.documentation_drift),
        ("Capability", drift.capability_drift),
        ("Knowledge", drift.knowledge_drift),
        ("RFC", drift.rfc_drift),
    ]:
        status = "⚠️ Elevated" if score > 30 else "✅ Normal"
        lines.append(f"| {dim} | {score}/100 | {status} |")
    lines.append("")

    if drift.details:
        lines.append("## Details")
        lines.append("")
        for detail in drift.details:
            lines.append(f"- {detail}")
        lines.append("")

    return "\n".join(lines)


def generate_confidence_report(confidence: ConfidenceResult) -> str:
    """Generate a confidence assessment report."""
    lines: list[str] = []
    lines.append("# Product Confidence Report")
    lines.append("")
    lines.append(f"**Overall Confidence:** {confidence.overall}/100")
    lines.append("")

    lines.append("## Confidence Dimensions")
    lines.append("")
    lines.append("| Dimension | Score |")
    lines.append("|-----------|-------|")
    lines.append(f"| State Confidence | {confidence.state_confidence}/100 |")
    lines.append(f"| Release Confidence | {confidence.release_confidence}/100 |")
    lines.append(f"| Data Quality | {confidence.data_quality}/100 |")
    lines.append(f"| Coverage | {confidence.coverage_confidence}/100 |")
    lines.append(f"| Timestamp Freshness | {confidence.timestamp_confidence}/100 |")
    lines.append("")

    if confidence.factors:
        lines.append("## Factors")
        lines.append("")
        for factor in confidence.factors:
            lines.append(f"- {factor}")
        lines.append("")

    return "\n".join(lines)


def generate_runtime_snapshot(
    state: ProductState, drift: DriftReport, confidence: ConfidenceResult
) -> str:
    """Generate a complete runtime snapshot report."""
    lines: list[str] = []
    lines.append("# Product State Runtime Snapshot")
    lines.append("")
    lines.append(f"**Generated:** {state.timestamp}")
    lines.append(f"**State:** {state.label}")
    lines.append(f"**Overall Health:** {state.overall_health}/100")
    lines.append(f"**Confidence:** {confidence.overall}/100")
    lines.append(f"**Drift:** {drift.overall_drift}/100")
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Product State | {state.label} |")
    lines.append(f"| Capabilities Complete | {state.capabilities_complete}/{state.total_capabilities} |")
    lines.append(f"| Overall Health | {state.overall_health}/100 |")
    lines.append(f"| Risk Score | {state.risk_score}/100 |")
    lines.append(f"| Release Readiness | {state.release_readiness}/100 |")
    lines.append(f"| Product Momentum | {state.product_momentum:+.1f} |")
    lines.append(f"| Technical Debt | {state.technical_debt} items |")
    lines.append(f"| Drift Score | {drift.overall_drift}/100 |")
    lines.append(f"| Confidence | {confidence.overall}/100 |")
    lines.append("")

    return "\n".join(lines)


def generate_release_confidence_report(state: ProductState, confidence: ConfidenceResult) -> str:
    """Generate a release confidence report."""
    lines: list[str] = []
    lines.append("# Release Confidence Report")
    lines.append("")
    lines.append(f"**State:** {state.label}")
    lines.append(f"**Health:** {state.overall_health}/100")
    lines.append(f"**Release Confidence:** {confidence.release_confidence}/100")
    lines.append(f"**State Confidence:** {confidence.state_confidence}/100")
    lines.append("")

    released = state.release_readiness >= 70 and confidence.release_confidence >= 70
    lines.append(f"**Assessment:** {'✅ Ready for release' if released else '⏳ Not yet ready'}")
    lines.append("")

    lines.append("## Release Criteria")
    lines.append("")
    lines.append("| Criteria | Current | Target | Met? |")
    lines.append("|----------|---------|-------|------|")
    lines.append(f"| Overall Health | {state.overall_health}/100 | 70/100 | {'✅' if state.overall_health >= 70 else '❌'} |")
    lines.append(f"| Release Readiness | {state.release_readiness}/100 | 70/100 | {'✅' if state.release_readiness >= 70 else '❌'} |")
    lines.append(f"| Release Confidence | {confidence.release_confidence}/100 | 70/100 | {'✅' if confidence.release_confidence >= 70 else '❌'} |")
    lines.append(f"| Capabilities Complete | {state.capabilities_complete}/{state.total_capabilities} | ≥80% | {'✅' if state.completion_percent >= 80 else '❌'} |")
    lines.append(f"| Blocking Debt | {state.blocking_debt} | 0 | {'✅' if state.blocking_debt == 0 else '❌'} |")
    lines.append("")

    if not released:
        lines.append("## Gaps")
        lines.append("")
        if state.overall_health < 70:
            lines.append(f"- Health {state.overall_health}/100 needs to reach 70/100")
        if state.release_readiness < 70:
            lines.append(f"- Release readiness {state.release_readiness}/100 needs to reach 70/100")
        if confidence.release_confidence < 70:
            lines.append(f"- Release confidence {confidence.release_confidence}/100 needs to reach 70/100")
        if state.completion_percent < 80:
            lines.append(f"- Capability completion {state.completion_percent}% needs to reach 80%")
        if state.blocking_debt > 0:
            lines.append(f"- {state.blocking_debt} blocking debt item(s) need to be resolved")
        lines.append("")

    return "\n".join(lines)
