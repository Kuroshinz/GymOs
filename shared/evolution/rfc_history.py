"""RFC History — analyzes the impact of RFCs on product evolution.

Stateless functions consuming Kernel state.
"""

from __future__ import annotations

from shared.capabilities import compute_platform_state
from shared.capabilities import registry as _cap_registry
from shared.capabilities.enums import CapabilityStatus
from shared.capabilities.health import calculate_health
from shared.evolution.evolution_engine import RfcImpactScore
from shared.kernel.kernel import KernelSnapshot
from shared.kernel.kernel_state import create_default_state


def _get_rfc_capability_mapping() -> dict[str, list[str]]:
    """Central mapping of RFC IDs to affected capability IDs.

    Must stay in sync with timeline._get_rfc_capability_mapping().
    """
    return {
        "RFC-018": ["capability-platform", "product-intelligence"],
        "RFC-018.5": [
            "capability-platform", "product-intelligence",
            "training-intelligence", "nutrition-intelligence",
            "knowledge-platform", "event-platform",
        ],
        "RFC-019": ["recovery-intelligence"],
    }


def compute_rfc_impact_scores(
    snapshots: list[KernelSnapshot] | None = None,
) -> list[RfcImpactScore]:
    """Compute impact scores for all known RFCs.

    Uses a weighted composite:
    - 40%: completion ratio (completed / affected)
    - 30%: average maturity gain per affected capability
    - 30%: overall product health delta
    """
    state = create_default_state()
    rfc_cap_map = _get_rfc_capability_mapping()
    cap_map = {c.capability_id: c for c in _cap_registry.list_all()}
    impacts: list[RfcImpactScore] = []

    state_ps = compute_platform_state(_cap_registry)
    health_delta = state_ps.overall_health

    for rfc_id, rfc in state.rfcs.items():
        affected_ids = rfc_cap_map.get(rfc_id, [])
        affected = len(affected_ids)
        completed = 0
        total_maturity = 0.0

        for cid in affected_ids:
            cap = cap_map.get(cid)
            if cap is None:
                continue
            if cap.status == CapabilityStatus.COMPLETE:
                completed += 1
            health = calculate_health(cap)
            total_maturity += health.overall

        # Weighted composite scoring
        completion_ratio = completed / max(affected, 1)
        avg_maturity = total_maturity / max(affected, 1)

        impact_score = (
            completion_ratio * 40 +
            min(avg_maturity, 100) * 0.30 +
            min(health_delta, 100) * 0.30
        )

        # Apply RFC status multiplier
        if rfc.status.name == "COMPLETE":
            impact_score *= 1.0
        elif rfc.status.name == "IN_PROGRESS":
            impact_score *= 0.5
        elif rfc.status.name == "DRAFT":
            impact_score *= 0.1

        impacts.append(RfcImpactScore(
            rfc_id=rfc_id,
            title=rfc.title,
            health_delta=round(health_delta, 1),
            capabilities_affected=affected,
            capabilities_completed=completed,
            maturity_gain=round(total_maturity, 1),
            impact_score=round(impact_score, 1),
        ))

    return sorted(impacts, key=lambda x: x.impact_score, reverse=True)


def find_most_impactful_rfc(
    impacts: list[RfcImpactScore],
) -> RfcImpactScore | None:
    """Find the RFC with the highest impact score."""
    if not impacts:
        return None
    return impacts[0]
