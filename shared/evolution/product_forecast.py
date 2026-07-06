"""Product Forecast — forecasts the product's evolution trajectory.

Combines capability velocity, RFC impacts, and release readiness
to produce a unified product-level forecast.
"""

from __future__ import annotations

from shared.capabilities import compute_platform_state
from shared.capabilities import registry as _cap_registry
from shared.evolution.evolution_engine import (
    EstimatedRemainingWork,
    ProductCompletion,
    ProductCompletionForecast,
)
from shared.evolution.forecast import (
    estimate_remaining_work,
    forecast_product_completion,
)
from shared.kernel.kernel import KernelSnapshot


def compute_product_completion() -> ProductCompletion:
    """Compute current product completion metrics."""
    state = compute_platform_state(_cap_registry)
    caps = _cap_registry.list_all()
    total = len(caps)
    pct = round((state.capabilities_complete / total) * 100, 1) if total else 0.0

    remaining_work = estimate_remaining_work()

    return ProductCompletion(
        total_capabilities=total,
        complete=state.capabilities_complete,
        in_progress=state.capabilities_in_progress,
        not_started=state.capabilities_not_started,
        completion_percent=pct,
        estimated_remaining_work=float(remaining_work.estimated_sprints),
    )


def compute_estimated_remaining_work() -> EstimatedRemainingWork:
    """Compute estimated work remaining to reach v1.0."""
    state = compute_platform_state(_cap_registry)
    total = max(state.total_capabilities, 1)
    remaining = state.capabilities_not_started + state.capabilities_in_progress

    # Rough estimate: 0.5 capabilities per sprint
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


def build_product_completion_forecast(
    snapshots: list[KernelSnapshot] | None = None,
) -> ProductCompletionForecast:
    """Build a complete product completion forecast."""
    return forecast_product_completion(snapshots)
