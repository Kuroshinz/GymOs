"""Forecast Engine — predicts future product and capability states.

Stateless pure functions. Data driven — not ML.
Uses simple extrapolation from snapshots and registry state.
"""

from __future__ import annotations

from shared.capabilities import compute_platform_state
from shared.capabilities import registry as _cap_registry
from shared.capabilities.enums import CapabilityMaturity, CapabilityStatus
from shared.evolution.evolution_engine import (
    CapabilityForecast,
    EstimatedRemainingWork,
    ProductCompletionForecast,
    ReleaseForecast,
)
from shared.kernel.kernel import KernelSnapshot
from shared.kernel.kernel_context import assess_release_readiness


def forecast_release(
    target_version: str,
    snapshots: list[KernelSnapshot] | None = None,
) -> ReleaseForecast:
    """Forecast readiness for a future release based on current trajectory."""
    state = compute_platform_state(_cap_registry)
    total = max(state.total_capabilities, 1)
    completion_pct = (state.capabilities_complete / total) * 100

    # Simple velocity: estimate sprints based on remaining capabilities
    remaining = state.capabilities_not_started + state.capabilities_in_progress
    caps_per_sprint = 0.5  # rough estimate: 1 capability per 2 sprints
    estimated_sprints = max(1, int(remaining / caps_per_sprint))

    # Predicted readiness: current readiness + projected improvement
    current_release = assess_release_readiness(_cap_registry, target_version)
    predicted_score = min(100, current_release.score + (estimated_sprints * 5))

    # Count remaining blockers
    blocker_count = 0
    for cap in _cap_registry.list_all():
        if cap.blocked_by:
            for b in cap.blocked_by:
                dep = _cap_registry.find(b)
                if dep and dep.status != CapabilityStatus.COMPLETE:
                    blocker_count += 1

    confidence = "low" if estimated_sprints > 10 else "medium" if estimated_sprints > 4 else "high"

    return ReleaseForecast(
        target_version=target_version,
        predicted_readiness_score=round(min(predicted_score, 100), 1),
        predicted_completion_percent=round(min(100, completion_pct + estimated_sprints * 8), 1),
        estimated_sprints_remaining=estimated_sprints,
        blockers_remaining=blocker_count,
        confidence=confidence,
    )


def forecast_capability(
    capability_id: str,
    snapshots: list[KernelSnapshot] | None = None,
) -> CapabilityForecast:
    """Forecast the future maturity of a single capability."""
    cap = _cap_registry.find(capability_id)
    if cap is None:
        return CapabilityForecast(capability_id=capability_id, confidence="low")

    from shared.capabilities.health import calculate_health
    health = calculate_health(cap)
    current_maturity = health.overall

    levels = list(CapabilityMaturity)
    try:
        target_idx = levels.index(cap.target_maturity)
        current_idx = levels.index(cap.current_maturity)
        gap = max(target_idx - current_idx, 0)
    except ValueError:
        gap = 1

    # Rough estimate: 1 maturity level per 2-3 sprints
    sprints_to_target = gap * 3
    predicted_maturity = min(100, current_maturity + (sprints_to_target * 5))

    confidence = "low" if sprints_to_target > 15 else "medium" if sprints_to_target > 6 else "high"

    return CapabilityForecast(
        capability_id=capability_id,
        name=cap.name,
        current_maturity=round(current_maturity, 1),
        predicted_maturity=round(predicted_maturity, 1),
        sprints_to_target=sprints_to_target,
        confidence=confidence,
    )


def forecast_product_completion(
    snapshots: list[KernelSnapshot] | None = None,
) -> ProductCompletionForecast:
    """Forecast the product completion trajectory toward v1.0."""
    state = compute_platform_state(_cap_registry)
    total = max(state.total_capabilities, 1)
    current_pct = (state.capabilities_complete / total) * 100

    # v1.0 requires ~20 capabilities (estimate)
    v1_total = 20
    v1_remaining = v1_total - state.capabilities_complete
    caps_per_sprint = 0.5
    sprints_to_v1 = max(1, int(v1_remaining / caps_per_sprint))

    # Next RFC adds ~2 capabilities
    next_pct = ((state.capabilities_complete + 2) / total) * 100

    # Health forecast: gradual improvement
    health_at_v1 = min(90, state.overall_health + sprints_to_v1 * 2)

    confidence = "low" if sprints_to_v1 > 20 else "medium"

    return ProductCompletionForecast(
        current_completion=round(current_pct, 1),
        predicted_completion_next_rfc=round(min(next_pct, 100), 1),
        predicted_completion_v1=100.0,
        sprints_to_v1=sprints_to_v1,
        estimated_health_at_v1=round(health_at_v1, 1),
        confidence=confidence,
    )


def estimate_remaining_work() -> EstimatedRemainingWork:
    """Estimate remaining work to complete the product."""
    state = compute_platform_state(_cap_registry)
    total = max(state.total_capabilities, 1)
    remaining = state.capabilities_not_started + state.capabilities_in_progress

    caps_per_sprint = 0.5
    estimated_sprints = max(1, int(remaining / caps_per_sprint))
    estimated_weeks = estimated_sprints * 2

    confidence = "low" if estimated_sprints > 10 else "medium" if estimated_sprints > 4 else "high"

    return EstimatedRemainingWork(
        total_capabilities=total,
        remaining=remaining,
        estimated_sprints=estimated_sprints,
        estimated_weeks=estimated_weeks,
        confidence=confidence,
    )
