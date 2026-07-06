"""Capability History — analyzes how individual capabilities evolve.

Extends the Kernel's history module with evolution-specific analysis.
"""

from __future__ import annotations

from shared.capabilities import registry as _cap_registry
from shared.capabilities.enums import CapabilityStatus
from shared.capabilities.health import calculate_health
from shared.evolution.evolution_engine import (
    CapabilityVelocity,
    EvolutionVelocity,
    RfcContribution,
)
from shared.kernel.kernel import KernelSnapshot
from shared.kernel.kernel_state import create_default_state


def compute_capability_velocities(
    snapshots: list[KernelSnapshot] | None = None,
) -> list[CapabilityVelocity]:
    """Compute velocity for every capability."""
    velocities: list[CapabilityVelocity] = []

    for cap in _cap_registry.list_all():
        health = calculate_health(cap)
        maturity_gain = health.overall  # current health as a proxy for maturity

        # How many snapshots show this capability?
        time_periods = 0
        if snapshots:
            for s in snapshots:
                for m in s.metrics:
                    if m.capability_id == cap.capability_id:
                        time_periods += 1

        periods = max(time_periods, 1)
        velocity = round(maturity_gain / periods, 1)

        # Growth rate from snapshots
        growth_rate = 0.0
        if snapshots and time_periods >= 2:
            first_val: float | None = None
            last_val: float | None = None
            for s in snapshots:
                for m in s.metrics:
                    if m.capability_id == cap.capability_id:
                        if first_val is None:
                            first_val = m.runtime_maturity
                        last_val = m.runtime_maturity
            if first_val and first_val > 0 and last_val is not None:
                growth_rate = round(((last_val - first_val) / first_val) * 100, 1)

        velocities.append(CapabilityVelocity(
            capability_id=cap.capability_id,
            name=cap.name,
            maturity_gain=round(maturity_gain, 1),
            time_periods=time_periods,
            velocity=velocity,
            growth_rate=growth_rate,
        ))

    return velocities


def find_fastest_capability(
    velocities: list[CapabilityVelocity],
) -> CapabilityVelocity | None:
    """Find the capability with the highest velocity."""
    if not velocities:
        return None
    return max(velocities, key=lambda v: v.velocity)


def find_slowest_capability(
    velocities: list[CapabilityVelocity],
) -> CapabilityVelocity | None:
    """Find the capability with the lowest velocity."""
    if not velocities:
        return None
    return min(velocities, key=lambda v: v.velocity)


# ── Evolution Velocity ──────────────────────────────────────────────────────


def compute_evolution_velocity(
    snapshots: list[KernelSnapshot] | None = None,
) -> EvolutionVelocity:
    """Compute product-wide evolution velocity."""
    from shared.evolution.rfc_history import compute_rfc_impact_scores

    state = create_default_state()
    caps = _cap_registry.list_all()

    completed_rfcs = sum(1 for r in state.rfcs.values() if r.status.name == "COMPLETE")
    completed_caps = sum(1 for c in caps if c.status == CapabilityStatus.COMPLETE)

    total_maturity = 0.0
    for cap in caps:
        health = calculate_health(cap)
        total_maturity += health.overall
    avg_maturity = total_maturity / max(len(caps), 1)

    rfc_impact_sum = sum(
        rfc.impact_score for rfc in compute_rfc_impact_scores(snapshots)
    )

    velocity_score = (
        completed_caps * 10 +
        completed_rfcs * 15 +
        avg_maturity * 0.3 +
        rfc_impact_sum * 0.1
    )

    return EvolutionVelocity(
        period_label="current",
        maturity_delta=round(avg_maturity, 1),
        capabilities_completed=completed_caps,
        rfc_impact_sum=round(rfc_impact_sum, 1),
        velocity_score=round(velocity_score, 1),
    )


def compute_rfc_contributions(
    snapshots: list[KernelSnapshot] | None = None,
) -> list[RfcContribution]:
    """Compute each RFC's contribution to product evolution."""
    from shared.evolution.rfc_history import compute_rfc_impact_scores

    state = create_default_state()
    impacts = compute_rfc_impact_scores(snapshots)
    total_impact = sum(i.impact_score for i in impacts) or 1

    caps = _cap_registry.list_all()
    total_caps = max(len(caps), 1)
    completed_caps = sum(1 for c in caps if c.status == CapabilityStatus.COMPLETE)

    contributions: list[RfcContribution] = []
    for impact in impacts:
        rfc = state.rfcs.get(impact.rfc_id)
        contribution_pct = round((impact.impact_score / total_impact) * 100, 1)

        contributions.append(RfcContribution(
            rfc_id=impact.rfc_id,
            rfc_title=impact.title,
            status=rfc.status.name if rfc else "unknown",
            capabilities_affected=impact.capabilities_affected,
            maturity_contribution=round(impact.maturity_gain, 1),
            completion_contribution=round(
                (impact.capabilities_completed / total_caps) * 100, 1
            ),
            contribution_percent=contribution_pct,
        ))

    return contributions
