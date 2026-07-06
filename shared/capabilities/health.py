"""Health Engine — computes health scores for capabilities and platform.

Stateless, deterministic functions operating on Capability data.
"""

from __future__ import annotations

from shared.capabilities.capability import Capability
from shared.capabilities.enums import CapabilityMaturity, CapabilityStatus
from shared.capabilities.metrics import HealthScore, MetricResult


def score_maturity(capability: Capability) -> float:
    """Score how close current maturity is to target maturity (0-100)."""
    levels = list(CapabilityMaturity)
    try:
        current_idx = levels.index(capability.current_maturity)
        target_idx = levels.index(capability.target_maturity)
    except ValueError:
        return 0.0
    if target_idx == 0:
        return 100.0
    return min((current_idx / target_idx) * 100.0, 100.0)


def score_architecture(capability: Capability) -> float:
    """Architecture health based on maturity and status."""
    base = 0.0
    if capability.status == CapabilityStatus.COMPLETE:
        base = 90.0
    elif capability.status == CapabilityStatus.IN_PROGRESS:
        base = 50.0
    elif capability.status == CapabilityStatus.NOT_STARTED:
        base = 0.0
    if capability.status == CapabilityStatus.BLOCKED:
        base = 20.0

    maturity_bonus = score_maturity(capability) * 0.1
    return min(base + maturity_bonus, 100.0)


def score_tests(capability: Capability) -> float:
    """Test health from completion metrics."""
    if capability.completion.total_tasks == 0:
        return 0.0
    return capability.completion.current_percent


def score_documentation(capability: Capability) -> float:
    """Documentation health based on presence of key docs."""
    score = 0.0
    if capability.description:
        score += 20.0
    if capability.documentation_links:
        score += 30.0
    if capability.last_review:
        score += 25.0
    if capability.current_maturity.value >= CapabilityMaturity.IMPLEMENTED.value:
        score += 25.0
    return min(score, 100.0)


def score_platform(capability: Capability) -> float:
    """Platform integration health — dependencies, debt, risk."""
    score = 50.0
    debt = capability.technical_debt
    if debt.blocking_count == 0:
        score += 20.0
    else:
        score -= 10.0 * debt.blocking_count

    if capability.risk_level.value <= 2:  # LOW or MEDIUM
        score += 15.0
    else:
        score -= 15.0
    return max(min(score, 100.0), 0.0)


def calculate_health(capability: Capability) -> HealthScore:
    """Compute full health profile for a single capability."""
    arch = score_architecture(capability)
    tests = score_tests(capability)
    docs = score_documentation(capability)
    plat = score_platform(capability)
    overall = (arch * 0.30 + tests * 0.25 + docs * 0.20 + plat * 0.25)

    metrics = (
        MetricResult(label="Architecture", score=arch, target=90.0),
        MetricResult(label="Test Coverage", score=tests, target=85.0),
        MetricResult(label="Documentation", score=docs, target=80.0),
        MetricResult(label="Platform Integration", score=plat, target=80.0),
    )
    return HealthScore(
        overall=round(overall, 1),
        architecture=round(arch, 1),
        test_coverage=round(tests, 1),
        documentation=round(docs, 1),
        platform=round(plat, 1),
        sub_scores=metrics,
    )
