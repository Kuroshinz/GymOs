"""Kernel Context — aggregates capability platform data into runtime context.

This is the bridge between the Capability Platform (shared/capabilities/)
and the Kernel. It consumes capability data and produces kernel views.
"""

from __future__ import annotations

from shared.capabilities import (
    CapabilityMaturity,
    CapabilityStatus,
    compute_platform_state,
)
from shared.capabilities.capability import Capability
from shared.capabilities.health import (
    calculate_health,
    score_documentation,
    score_tests,
)
from shared.capabilities.registry import CapabilityRegistry as Registry
from shared.kernel.kernel import (
    KernelRuntime,
    ProductPhase,
    ReleaseReadiness,
    ReleaseReadinessResult,
    RoadmapStage,
    RuntimeMetrics,
)
from shared.version import APP_VERSION


def build_runtime_metrics(registry: Registry) -> list[RuntimeMetrics]:
    """Build runtime metrics for each capability using actual computed health."""
    metrics: list[RuntimeMetrics] = []
    for cap in registry.list_all():
        health = calculate_health(cap)
        arch = health.architecture
        docs = health.documentation
        test = health.test_coverage
        cov = cap.completion.current_percent

        # Runtime maturity: weighted from sub-scores
        runtime_maturity = (
            arch * 0.25 +
            docs * 0.15 +
            test * 0.20 +
            cov * 0.15 +
            (100 - min(cap.technical_debt.total_items * 5, 100)) * 0.10 +
            _dependency_health(cap, registry) * 0.15
        )

        debt_score = max(0, 100 - cap.technical_debt.total_items * 5)
        dep_health = _dependency_health(cap, registry)

        metrics.append(RuntimeMetrics(
            capability_id=cap.capability_id,
            name=cap.name,
            runtime_maturity=round(runtime_maturity, 1),
            architecture_score=round(arch, 1),
            documentation_score=round(docs, 1),
            test_score=round(test, 1),
            coverage_score=round(cov, 1),
            completion_score=round(cov, 1),
            debt_score=round(debt_score, 1),
            dependency_health=round(dep_health, 1),
        ))
    return metrics


def _dependency_health(cap: Capability, reg: Registry) -> float:
    """Score how healthy a capability's dependencies are (0-100)."""
    if not cap.dependencies:
        return 100.0
    scores: list[float] = []
    for dep_id in cap.dependencies:
        dep = reg.find(dep_id)
        if dep is None:
            scores.append(0.0)
        else:
            dep_health = calculate_health(dep)
            scores.append(dep_health.overall)
    if not scores:
        return 100.0
    return sum(scores) / len(scores)


def build_kernel_runtime(reg: Registry) -> KernelRuntime:
    """Build the current kernel runtime from capability platform data."""
    state = compute_platform_state(reg)

    return KernelRuntime(
        version=APP_VERSION,
        phase=ProductPhase.ALPHA,
        roadmap_stage=RoadmapStage.FOUNDATION,
        current_rfc="RFC-020.9",
        next_rfc="RFC-021",
        total_capabilities=state.total_capabilities,
        capabilities_complete=state.capabilities_complete,
        capabilities_in_progress=state.capabilities_in_progress,
        capabilities_not_started=state.capabilities_not_started,
        capabilities_blocked=state.capabilities_blocked,
        overall_health=round(state.overall_health, 1),
        weakest_capability=state.weakest_capability,
        strongest_capability=state.strongest_capability,
        total_technical_debt=state.total_technical_debt,
        blocking_debt=state.blocking_debt,
        timestamp="",
    )


def assess_release_readiness(
    reg: Registry,
    target_version: str,
    required_capabilities: tuple[str, ...] = (),
) -> ReleaseReadinessResult:
    """Assess whether the platform is ready for a release."""
    state = compute_platform_state(reg)

    # Component scores (each 0-100)
    blockers = _find_blockers(reg)
    blocker_count = len(blockers)

    total_caps = max(state.total_capabilities, 1)
    cap_completion = (state.capabilities_complete / total_caps) * 100

    doc_score = _average_documentation(reg)
    test_score = _average_test_coverage(reg)
    health_score = state.overall_health

    max_debt = max(state.total_technical_debt, 1)
    debt_score = max(0, 100 - (state.blocking_debt / max_debt) * 100)

    # Weighted release score
    score = (
        cap_completion * 0.30 +
        doc_score * 0.15 +
        test_score * 0.20 +
        health_score * 0.20 +
        debt_score * 0.15
    )

    # Blocker penalty
    score -= blocker_count * 10

    score = max(0, min(100, score))

    # Readiness level
    if score >= 75 and blocker_count == 0:
        readiness = ReleaseReadiness.READY
    elif score >= 40:
        readiness = ReleaseReadiness.ALMOST_READY
    else:
        readiness = ReleaseReadiness.NOT_READY

    # Gap analysis
    gaps: list[str] = []
    for cap in reg.list_all():
        if cap.status == CapabilityStatus.NOT_STARTED:
            gaps.append(f"{cap.name} not started")
        elif cap.status == CapabilityStatus.IN_PROGRESS:
            try:
                levels = list(CapabilityMaturity)
                if levels.index(cap.current_maturity) < levels.index(cap.target_maturity):
                    gaps.append(f"{cap.name}: {cap.current_maturity.name} -> {cap.target_maturity.name}")
            except ValueError:
                gaps.append(f"{cap.name}: maturity scoring issue")

    return ReleaseReadinessResult(
        version=target_version,
        readiness=readiness,
        score=round(score, 1),
        blockers=tuple(blockers),
        blocker_count=blocker_count,
        capability_completion=round(cap_completion, 1),
        documentation_score=round(doc_score, 1),
        test_score=round(test_score, 1),
        health_score=round(health_score, 1),
        debt_score=round(debt_score, 1),
        gaps=tuple(gaps),
    )


def _find_blockers(reg: Registry) -> list[str]:
    """Find blocking issues across capabilities."""
    blockers: list[str] = []
    for cap in reg.list_all():
        if cap.blocked_by:
            for b in cap.blocked_by:
                blockers.append(f"{cap.name} blocked by {b}")
        if cap.status == CapabilityStatus.BLOCKED:
            blockers.append(f"{cap.name} is blocked")
    return blockers


def _average_documentation(reg: Registry) -> float:
    """Average documentation health across all capabilities."""
    caps = reg.list_all()
    if not caps:
        return 0.0
    scores = [score_documentation(c) for c in caps]
    return sum(scores) / len(scores)


def _average_test_coverage(reg: Registry) -> float:
    """Average test coverage across all capabilities."""
    caps = reg.list_all()
    if not caps:
        return 0.0
    scores = [score_tests(c) for c in caps]
    return sum(scores) / len(scores)
