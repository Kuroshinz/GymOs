"""Kernel History — in-memory capability evolution tracking.

Maintains snapshots and computes trends, growth rates, and timelines.
Stateless — data is passed in, not stored globally.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from shared.kernel.kernel import (
    CapabilityTrend,
    KernelSnapshot,
    KernelSnapshotType,
    TrendPoint,
)


@dataclass
class HistoryStore:
    """In-memory store of kernel snapshots for trend analysis."""

    snapshots: list[KernelSnapshot] = field(default_factory=list)

    def record(self, snapshot: KernelSnapshot) -> None:
        self.snapshots.append(snapshot)

    def get_all(self) -> list[KernelSnapshot]:
        return list(self.snapshots)

    def get_by_type(self, snapshot_type: KernelSnapshotType) -> list[KernelSnapshot]:
        return [s for s in self.snapshots if s.snapshot_type == snapshot_type]

    def get_latest(self) -> KernelSnapshot | None:
        if not self.snapshots:
            return None
        return self.snapshots[-1]

    def clear(self) -> None:
        self.snapshots.clear()


def compute_timeline(snapshots: list[KernelSnapshot]) -> list[dict]:
    """Build a human-readable timeline from snapshots."""
    timeline: list[dict] = []
    for s in snapshots:
        timeline.append({
            "timestamp": s.timestamp,
            "type": s.snapshot_type.name,
            "overall_health": s.overall_health,
            "total_capabilities": s.runtime.total_capabilities,
            "complete": s.runtime.capabilities_complete,
            "weakest": s.runtime.weakest_capability,
            "strongest": s.runtime.strongest_capability,
        })
    return timeline


def compute_trend_for_capability(
    snapshots: list[KernelSnapshot],
    capability_id: str,
) -> CapabilityTrend:
    """Compute trend data for a single capability across snapshots."""
    points: list[TrendPoint] = []
    name = ""

    for s in snapshots:
        for m in s.metrics:
            if m.capability_id == capability_id:
                name = m.name
                points.append(TrendPoint(
                    timestamp=s.timestamp,
                    value=m.runtime_maturity,
                    label=m.name,
                ))

    growth_rate = _compute_growth_rate(points)

    return CapabilityTrend(
        capability_id=capability_id,
        name=name,
        points=tuple(points),
        growth_rate=growth_rate,
    )


def compute_all_trends(snapshots: list[KernelSnapshot]) -> list[CapabilityTrend]:
    """Compute trends for all capabilities across snapshots."""
    if not snapshots:
        return []

    cap_ids = {m.capability_id for s in snapshots for m in s.metrics}
    return [compute_trend_for_capability(snapshots, cid) for cid in cap_ids]


def compute_platform_trend(snapshots: list[KernelSnapshot]) -> CapabilityTrend:
    """Compute the overall platform health trend."""
    points: list[TrendPoint] = []
    for s in snapshots:
        points.append(TrendPoint(
            timestamp=s.timestamp,
            value=s.overall_health,
            label="Platform Overall Health",
        ))
    growth_rate = _compute_growth_rate(points)

    return CapabilityTrend(
        capability_id="_platform",
        name="Platform Overall",
        points=tuple(points),
        growth_rate=growth_rate,
    )


def _compute_growth_rate(points: list[TrendPoint]) -> float:
    """Simple growth rate: (last - first) / first * 100, or 0 if no data."""
    if len(points) < 2:
        return 0.0
    first = points[0].value
    last = points[-1].value
    if first == 0:
        return 0.0
    return round(((last - first) / first) * 100, 1)
