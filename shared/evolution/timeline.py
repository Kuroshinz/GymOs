"""Timeline module — constructs evolution, RFC, and capability growth timelines.

Stateless pure functions consuming Kernel and Capability Platform data.
"""

from __future__ import annotations

from shared.capabilities import registry as _cap_registry
from shared.capabilities.enums import CapabilityStatus
from shared.evolution.capability_history import (
    compute_capability_velocities,
    compute_evolution_velocity,
    compute_rfc_contributions,
    find_fastest_capability,
    find_slowest_capability,
)
from shared.evolution.evolution_engine import (
    CapabilityGrowthTimeline,
    EvolutionChain,
    EvolutionChainLink,
    EvolutionSummary,
    EvolutionTimeline,
    RfcTimeline,
    TimelineEntry,
    VersionProgress,
)
from shared.evolution.milestone_graph import build_milestone_progress
from shared.evolution.product_forecast import compute_product_completion
from shared.kernel.kernel import (
    KernelSnapshot,
    Release,
    RfcRecord,
)
from shared.kernel.kernel_state import create_default_state


def build_evolution_timeline(
    snapshots: list[KernelSnapshot],
    rfcs: list[RfcRecord],
    releases: list[Release],
) -> EvolutionTimeline:
    """Build a complete evolution timeline from all available data."""
    entries: list[TimelineEntry] = []

    # RFC events
    for rfc in rfcs:
        entries.append(TimelineEntry(
            timestamp=rfc.created_at or "unknown",
            event_type="rfc",
            label=f"RFC {rfc.rfc_id}: {rfc.title}",
            description=rfc.status.name,
        ))

    # Release events
    for release in releases:
        entries.append(TimelineEntry(
            timestamp=release.release_date or "unknown",
            event_type="release",
            label=f"v{release.version}: {release.name}",
            description="Released" if release.is_released else "Planned",
        ))

    # Snapshot events
    for snapshot in snapshots:
        entry_label = f"Snapshot: {snapshot.runtime.capabilities_complete}/{snapshot.runtime.total_capabilities} complete"
        entries.append(TimelineEntry(
            timestamp=snapshot.timestamp,
            event_type="snapshot",
            label=entry_label,
            description=snapshot.snapshot_type.name,
            value=snapshot.overall_health,
        ))

    entries.sort(key=lambda e: (e.timestamp, e.event_type))
    return EvolutionTimeline(entries=tuple(entries))


def build_rfc_timeline(rfcs: list[RfcRecord]) -> RfcTimeline:
    """Build a timeline of RFC events."""
    entries: list[TimelineEntry] = []
    for rfc in rfcs:
        entries.append(TimelineEntry(
            timestamp=rfc.created_at or "unknown",
            event_type="rfc",
            label=f"{rfc.rfc_id}: {rfc.title}",
            description=rfc.status.name,
        ))
    entries.sort(key=lambda e: e.timestamp)
    return RfcTimeline(entries=tuple(entries))


def build_capability_growth_timeline(
    snapshots: list[KernelSnapshot],
) -> CapabilityGrowthTimeline:
    """Build a timeline of capability growth across snapshots."""
    entries: list[TimelineEntry] = []

    for snapshot in snapshots:
        for metric in snapshot.metrics:
            entries.append(TimelineEntry(
                timestamp=snapshot.timestamp,
                event_type="capability_growth",
                label=f"{metric.name}: {metric.runtime_maturity}",
                description=f"Maturity {metric.runtime_maturity}",
                value=metric.runtime_maturity,
            ))

    entries.sort(key=lambda e: (e.timestamp, e.label))
    return CapabilityGrowthTimeline(entries=tuple(entries))


def build_version_progress() -> list[VersionProgress]:
    """Build progress data for all known versions."""
    caps = _cap_registry.list_all()
    total = len(caps)
    complete = sum(1 for c in caps if c.status == CapabilityStatus.COMPLETE)
    pct = round((complete / total) * 100, 1) if total else 0.0

    from shared.capabilities import compute_platform_state
    state = compute_platform_state(_cap_registry)

    return [
        VersionProgress(
            version="0.5.0",
            total_capabilities=total,
            complete=complete,
            completion_percent=pct,
            health_score=round(state.overall_health, 1),
        ),
    ]


# ── Evolution Chain (RFC → Capability → Milestone → Version) ──────────────


def _get_rfc_capability_mapping() -> dict[str, list[str]]:
    """Map RFC IDs to the capability IDs they affect.

    This central mapping drives the evolution chain and impact analysis.
    Extend this when new RFCs are defined.
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


def _get_capability_milestone_mapping() -> dict[str, str]:
    """Map capability IDs to their target milestone version."""
    milestones = build_milestone_progress()
    mapping: dict[str, str] = {}
    for m in milestones:
        for cid in m.capabilities_required:
            mapping[cid] = m.target_version
    return mapping


def build_evolution_chain(
    snapshots: list[KernelSnapshot] | None = None,
) -> EvolutionChain:
    """Build the full RFC → Capability → Milestone → Version chain."""
    state = create_default_state()
    caps = {c.capability_id: c for c in _cap_registry.list_all()}
    rfc_cap_map = _get_rfc_capability_mapping()
    cap_milestone_map = _get_capability_milestone_mapping()

    links: list[EvolutionChainLink] = []

    for rfc_id, rfc in state.rfcs.items():
        affected_caps = rfc_cap_map.get(rfc_id, [])
        for cap_id in affected_caps:
            cap = caps.get(cap_id)
            milestone_version = cap_milestone_map.get(cap_id, "future")
            release = state.releases.get(milestone_version)

            links.append(EvolutionChainLink(
                rfc_id=rfc_id,
                rfc_title=rfc.title,
                rfc_status=rfc.status.name,
                capability_id=cap_id,
                capability_name=cap.name if cap else cap_id,
                capability_status=cap.status.name if cap else "unknown",
                capability_maturity=cap.current_maturity.name if cap else "unknown",
                milestone_label=release.name if release else "Future Release",
                milestone_version=milestone_version,
                version_name=release.name if release else "Planned",
                version_is_released=release.is_released if release else False,
            ))

    return EvolutionChain(links=tuple(links))


def build_evolution_summary(
    snapshots: list[KernelSnapshot] | None = None,
) -> EvolutionSummary:
    """Build a comprehensive summary of all evolution data."""
    state = create_default_state()
    velocities = compute_capability_velocities(snapshots)
    impacts = compute_rfc_contributions(snapshots)

    milestones = build_milestone_progress()
    reached = sum(1 for m in milestones if m.is_reached)

    completed_rfcs = sum(1 for r in state.rfcs.values() if r.status.name == "COMPLETE")
    released = sum(1 for r in state.releases.values() if r.is_released)

    fastest = find_fastest_capability(velocities)
    slowest = find_slowest_capability(velocities)
    most_impactful = impacts[0] if impacts else None

    completion = compute_product_completion()
    velocity = compute_evolution_velocity(snapshots)

    return EvolutionSummary(
        total_rfcs=len(state.rfcs),
        completed_rfcs=completed_rfcs,
        total_capabilities=completion.total_capabilities,
        completed_capabilities=completion.complete,
        total_milestones=len(milestones),
        reached_milestones=reached,
        total_versions=len(state.releases),
        released_versions=released,
        overall_evolution_progress=completion.completion_percent,
        evolution_velocity=velocity,
        fastest_capability=fastest.name if fastest else "",
        slowest_capability=slowest.name if slowest else "",
        most_impactful_rfc=most_impactful.rfc_id if most_impactful else "",
    )
