"""Kernel Health — multi-dimensional product health assessment.

Combines capability health data with platform-level health dimensions.
"""

from __future__ import annotations

from shared.capabilities import compute_platform_state
from shared.capabilities import registry as _cap_registry
from shared.capabilities.health import (
    calculate_health,
    score_documentation,
    score_tests,
)
from shared.kernel.kernel import ProductHealth
from shared.kernel.kernel_context import assess_release_readiness


def compute_product_health() -> ProductHealth:
    """Compute all health dimensions for the product."""
    state = compute_platform_state(_cap_registry)
    caps = _cap_registry.list_all()
    release = assess_release_readiness(_cap_registry, "0.5.0")

    if not caps:
        return ProductHealth(overall=0.0, architecture_health=0.0, engineering_health=0.0,
                             knowledge_health=0.0, capability_health=0.0, documentation_health=0.0)

    n = len(caps)

    # Architecture health: average of architecture sub-scores
    arch_health = sum(calculate_health(c).architecture for c in caps) / n

    # Engineering health: average test coverage
    eng_health = sum(score_tests(c) for c in caps) / n

    # Knowledge health: average completion + runtime maturity proxy
    knowledge_health = sum(c.completion.current_percent for c in caps) / n

    # Capability health: overall platform state
    cap_health = state.overall_health

    # Documentation health
    doc_health = sum(score_documentation(c) for c in caps) / n

    # Overall: weighted combination
    overall = (
        arch_health * 0.20 +
        eng_health * 0.20 +
        knowledge_health * 0.15 +
        cap_health * 0.25 +
        doc_health * 0.10 +
        release.score * 0.10
    )

    return ProductHealth(
        overall=round(overall, 1),
        architecture_health=round(arch_health, 1),
        engineering_health=round(eng_health, 1),
        knowledge_health=round(knowledge_health, 1),
        capability_health=round(cap_health, 1),
        documentation_health=round(doc_health, 1),
    )
