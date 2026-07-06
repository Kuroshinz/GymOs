"""Kernel State — tracks product identity, RFC lifecycle, release history.

Consumes the Capability Platform for capability data.
Adds product-level state not tracked by capabilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from shared.kernel.kernel import (
    ProductIdentity,
    Release,
    ReleaseReadinessResult,
    RfcRecord,
    RfcStatus,
)


@dataclass
class KernelState:
    """Mutable kernel state — the source of truth for all product-level state."""

    # Product identity (immutable)
    identity: ProductIdentity = field(default_factory=ProductIdentity)

    # RFC registry
    rfcs: dict[str, RfcRecord] = field(default_factory=dict)

    # Release history
    releases: dict[str, Release] = field(default_factory=dict)

    # Current tracking
    current_rfc: str = ""
    next_rfc: str = ""
    current_release: str = "0.5.0"
    current_milestone: str = "Platform Maturity"

    # Active release readiness
    release_readiness: ReleaseReadinessResult | None = None

    def register_rfc(self, rfc: RfcRecord) -> None:
        if rfc.rfc_id in self.rfcs:
            raise ValueError(f"RFC {rfc.rfc_id} already registered")
        self.rfcs[rfc.rfc_id] = rfc

    def update_rfc_status(self, rfc_id: str, status: RfcStatus) -> None:
        if rfc_id not in self.rfcs:
            raise ValueError(f"RFC {rfc_id} not found")
        old = self.rfcs[rfc_id]
        self.rfcs[rfc_id] = RfcRecord(
            rfc_id=old.rfc_id,
            title=old.title,
            status=status,
            description=old.description,
            depends_on=old.depends_on,
            created_at=old.created_at,
            completed_at=old.completed_at,
        )

    def register_release(self, release: Release) -> None:
        if release.version in self.releases:
            raise ValueError(f"Release {release.version} already registered")
        self.releases[release.version] = release

    def get_active_rfcs(self) -> list[RfcRecord]:
        return [r for r in self.rfcs.values() if r.status in (RfcStatus.IN_PROGRESS, RfcStatus.APPROVED)]

    def get_completed_rfcs(self) -> list[RfcRecord]:
        return [r for r in self.rfcs.values() if r.status == RfcStatus.COMPLETE]

    def get_released_versions(self) -> list[str]:
        return sorted([v for v, r in self.releases.items() if r.is_released])


def create_default_state() -> KernelState:
    """Create a default KernelState with pre-registered RFCs and releases."""
    state = KernelState()

    state.register_rfc(RfcRecord(
        rfc_id="RFC-018",
        title="Capability Platform",
        status=RfcStatus.COMPLETE,
        description="Self-describing introspection layer for GymOS.",
        created_at="2026-07-03",
        completed_at="2026-07-03",
    ))

    state.register_rfc(RfcRecord(
        rfc_id="RFC-018.5",
        title="GymOS Kernel",
        status=RfcStatus.IN_PROGRESS,
        description="Product Operating System — orchestrates product identity, lifecycle, and evolution.",
        depends_on=("RFC-018",),
        created_at="2026-07-03",
    ))

    state.register_rfc(RfcRecord(
        rfc_id="RFC-019",
        title="Recovery Intelligence",
        status=RfcStatus.DRAFT,
        description="Sleep logging, HRV readiness, soreness tracking, recovery score, deload scheduling.",
        depends_on=("RFC-018.5",),
        created_at="2026-07-03",
    ))

    state.current_rfc = "RFC-018.5"
    state.next_rfc = "RFC-019"

    state.register_release(Release(
        version="0.5.0",
        name="Platform Maturity",
        rfc_ids=("RFC-018", "RFC-018.5"),
        capabilities=(
            "training-intelligence",
            "nutrition-intelligence",
            "knowledge-platform",
            "event-platform",
            "product-intelligence",
            "capability-platform",
        ),
        is_released=False,
    ))

    state.register_release(Release(
        version="0.6.0",
        name="Recovery Intelligence",
        rfc_ids=("RFC-019",),
        capabilities=("recovery-intelligence",),
        is_released=False,
    ))

    return state
