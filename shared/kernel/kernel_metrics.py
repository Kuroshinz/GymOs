"""Kernel Metrics — compute runtime metrics and aggregate platform measurements.

Stateless pure functions operating on capability registry data.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from shared.capabilities import registry as _cap_registry
from shared.capabilities.enums import CapabilityStatus
from shared.capabilities.health import calculate_health
from shared.kernel.kernel import RuntimeMetrics


@dataclass(frozen=True)
class AggregatedMetrics:
    """Aggregated platform-wide metrics."""
    total_capabilities: int
    avg_runtime_maturity: float
    avg_architecture: float
    avg_documentation: float
    avg_test_coverage: float
    avg_completion: float
    avg_debt_score: float
    avg_dependency_health: float
    total_technical_debt: int
    blocking_debt: int
    capability_breakdown: tuple[RuntimeMetrics, ...] = field(default_factory=tuple)


def compute_aggregated_metrics() -> AggregatedMetrics:
    """Compute platform-wide aggregated metrics from the capability registry."""
    from shared.kernel.kernel_context import build_runtime_metrics

    metrics = build_runtime_metrics(_cap_registry)
    if not metrics:
        return AggregatedMetrics(
            total_capabilities=0, avg_runtime_maturity=0.0,
            avg_architecture=0.0, avg_documentation=0.0,
            avg_test_coverage=0.0, avg_completion=0.0,
            avg_debt_score=0.0, avg_dependency_health=0.0,
            total_technical_debt=0, blocking_debt=0,
        )

    n = len(metrics)
    total_debt = sum(c.technical_debt.total_items for c in _cap_registry.list_all())
    blocking = sum(c.technical_debt.critical + c.technical_debt.high for c in _cap_registry.list_all())

    return AggregatedMetrics(
        total_capabilities=n,
        avg_runtime_maturity=round(sum(m.runtime_maturity for m in metrics) / n, 1),
        avg_architecture=round(sum(m.architecture_score for m in metrics) / n, 1),
        avg_documentation=round(sum(m.documentation_score for m in metrics) / n, 1),
        avg_test_coverage=round(sum(m.test_score for m in metrics) / n, 1),
        avg_completion=round(sum(m.completion_score for m in metrics) / n, 1),
        avg_debt_score=round(sum(m.debt_score for m in metrics) / n, 1),
        avg_dependency_health=round(sum(m.dependency_health for m in metrics) / n, 1),
        total_technical_debt=total_debt,
        blocking_debt=blocking,
        capability_breakdown=tuple(metrics),
    )


def compute_maturity_distribution() -> dict[str, int]:
    """Count capabilities at each maturity level."""
    dist: dict[str, int] = {}
    for cap in _cap_registry.list_all():
        level = cap.current_maturity.name
        dist[level] = dist.get(level, 0) + 1
    return dist


def compute_health_distribution() -> dict[str, int]:
    """Count capabilities at each health rating."""
    dist: dict[str, int] = {}
    for cap in _cap_registry.list_all():
        health = calculate_health(cap)
        dist[health.rating] = dist.get(health.rating, 0) + 1
    return dist


def compute_completion_rate() -> float:
    """Overall platform completion rate."""
    caps = _cap_registry.list_all()
    if not caps:
        return 0.0
    total = len(caps)
    complete = sum(1 for c in caps if c.status == CapabilityStatus.COMPLETE)
    return round((complete / total) * 100, 1)
