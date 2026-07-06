"""Product Indicators — computes individual indicators for the Product State Engine.

Each indicator is a pure function consuming canonical sources.
Never duplicates data — reads from Capability Platform, Kernel, Evolution Engine,
and Product Knowledge Graph.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from shared.capabilities import compute_platform_state
from shared.capabilities import registry as _cap_registry
from shared.capabilities.enums import CapabilityStatus
from shared.capabilities.health import calculate_health, score_documentation, score_tests
from shared.evolution import EvolutionOrchestrator
from shared.graph import build_graph
from shared.graph.health import GraphHealthAnalyzer
from shared.kernel.kernel import RfcStatus
from shared.kernel.kernel_context import assess_release_readiness
from shared.kernel.kernel_state import create_default_state


@dataclass(frozen=True)
class IndicatorSet:
    """Complete set of product indicators."""

    overall_health: float = 0.0
    architecture_health: float = 0.0
    documentation_health: float = 0.0
    test_health: float = 0.0
    capability_health: float = 0.0
    completion_percent: float = 0.0
    total_capabilities: int = 0
    complete: int = 0
    in_progress: int = 0
    not_started: int = 0
    blocked: int = 0
    total_debt: int = 0
    blocking_debt: int = 0
    blockers: tuple[str, ...] = ()
    release_readiness: float = 0.0
    release_blockers: tuple[str, ...] = ()
    product_momentum: float = 0.0
    risk_score: float = 0.0
    evolution_velocity: float = 0.0
    active_rfcs: int = 0
    completed_rfcs: int = 0
    graph_health: float = 0.0


def compute_indicators() -> IndicatorSet:
    """Compute all product indicators from canonical sources."""
    caps = _cap_registry.list_all()
    state = compute_platform_state(_cap_registry)

    # Health composites
    arch_health = _avg(lambda c: calculate_health(c).architecture, caps)
    doc_health = _avg(score_documentation, caps)
    test_health = _avg(score_tests, caps)
    cap_health = state.overall_health
    overall_health = round(arch_health * 0.25 + doc_health * 0.15 + test_health * 0.20 + cap_health * 0.40, 1)

    # Technical debt
    total_debt = sum(c.technical_debt.total_items for c in caps)
    blocking_debt = sum(c.technical_debt.critical + c.technical_debt.high for c in caps)

    # Blockers
    blockers = tuple(c.name for c in caps if c.status == CapabilityStatus.IN_PROGRESS and c.blocked_by)

    # Release readiness
    release = assess_release_readiness(_cap_registry, "0.5.0")

    # Product momentum
    orchestrator = EvolutionOrchestrator()
    velocity = orchestrator.get_evolution_velocity()

    # RFC status
    kernel_state = create_default_state()
    active_rfcs = sum(1 for r in kernel_state.rfcs.values() if r.status in (RfcStatus.IN_PROGRESS, RfcStatus.APPROVED))
    completed_rfcs = sum(1 for r in kernel_state.rfcs.values() if r.status == RfcStatus.COMPLETE)

    # Graph health
    try:
        graph = build_graph()
        graph_health = GraphHealthAnalyzer(graph).analyze().overall
    except Exception:
        graph_health = 0.0

    # Risk score
    risk_score = round(
        (100.0 - overall_health) * 0.4 + (100.0 - release.score) * 0.3 + (100.0 - min(cap_health, 100)) * 0.3, 1
    )

    return IndicatorSet(
        overall_health=overall_health,
        architecture_health=round(arch_health, 1),
        documentation_health=round(doc_health, 1),
        test_health=round(test_health, 1),
        capability_health=round(cap_health, 1),
        completion_percent=state.overall_health,
        total_capabilities=state.total_capabilities,
        complete=state.capabilities_complete,
        in_progress=state.capabilities_in_progress,
        not_started=state.capabilities_not_started,
        blocked=state.capabilities_blocked,
        total_debt=total_debt,
        blocking_debt=blocking_debt,
        blockers=blockers,
        release_readiness=release.score,
        release_blockers=release.blockers,
        product_momentum=round(velocity.velocity_score, 1),
        risk_score=risk_score,
        evolution_velocity=round(velocity.velocity_score, 1),
        active_rfcs=active_rfcs,
        completed_rfcs=completed_rfcs,
        graph_health=round(graph_health, 1),
    )


def _avg(func: Callable, items: list) -> float:
    if not items:
        return 0.0
    return sum(func(c) for c in items) / len(items)
