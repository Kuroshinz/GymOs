"""Version Graph — constructs version progress and readiness trend data.

Consumes Kernel and Capability Platform to produce version-level views.
"""

from __future__ import annotations

from shared.capabilities import compute_platform_state
from shared.capabilities import registry as _cap_registry
from shared.capabilities.enums import CapabilityStatus
from shared.evolution.evolution_engine import VersionProgress, VersionReadinessTrend
from shared.kernel.kernel import KernelSnapshot


def build_version_progress() -> list[VersionProgress]:
    """Build progress data for all known versions."""
    caps = _cap_registry.list_all()
    total = len(caps)
    complete = sum(1 for c in caps if c.status == CapabilityStatus.COMPLETE)
    pct = round((complete / total) * 100, 1) if total else 0.0

    state = compute_platform_state(_cap_registry)

    return [
        VersionProgress(
            version="0.5.0",
            total_capabilities=total,
            complete=complete,
            completion_percent=pct,
            health_score=round(state.overall_health, 1),
        ),
        VersionProgress(
            version="0.6.0",
            total_capabilities=total,
            complete=complete,
            completion_percent=round((complete / total) * 100, 1) if total else 0.0,
            health_score=round(state.overall_health, 1),
        ),
    ]


def build_version_readiness_trend(
    snapshots: list[KernelSnapshot] | None = None,
) -> list[VersionReadinessTrend]:
    """Build readiness trend across versions."""
    from shared.kernel.kernel_context import assess_release_readiness

    versions = ["0.5.0", "0.6.0", "1.0.0"]
    trends: list[VersionReadinessTrend] = []

    previous_score: float | None = None
    for version in versions:
        result = assess_release_readiness(_cap_registry, version)
        score = result.score

        direction = "stable"
        if previous_score is not None:
            if score > previous_score:
                direction = "improving"
            elif score < previous_score:
                direction = "declining"

        delta = score - previous_score if previous_score is not None else 0.0

        trends.append(VersionReadinessTrend(
            version=version,
            readiness_score=round(score, 1),
            trend_direction=direction,
            delta=round(delta, 1),
        ))
        previous_score = score

    return trends
