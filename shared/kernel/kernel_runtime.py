"""Kernel Runtime — orchestrates kernel lifecycle.

Sits above kernel_state and kernel_context to provide a unified
runtime for consuming product-level information.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from shared.capabilities import registry as _cap_registry
from shared.kernel.kernel import (
    KernelRuntime,
    KernelSnapshot,
    KernelSnapshotType,
    ProductHealth,
    ReleaseReadinessResult,
    RuntimeMetrics,
)
from shared.kernel.kernel_context import (
    assess_release_readiness,
    build_kernel_runtime,
    build_runtime_metrics,
)
from shared.kernel.kernel_state import KernelState, create_default_state


@dataclass
class KernelRuntimeOrchestrator:
    """Unified kernel runtime — the primary entry point for kernel consumers."""

    state: KernelState = field(default_factory=create_default_state)
    snapshots: list[KernelSnapshot] = field(default_factory=list)
    debt_items: list = field(default_factory=list)

    def get_runtime(self) -> KernelRuntime:
        return build_kernel_runtime(_cap_registry)

    def get_metrics(self) -> list[RuntimeMetrics]:
        return build_runtime_metrics(_cap_registry)

    def get_product_health(self) -> ProductHealth:
        return self._compute_product_health()

    def assess_release(self, target_version: str = "") -> ReleaseReadinessResult:
        version = target_version or self.state.current_release
        return assess_release_readiness(_cap_registry, version)

    def take_snapshot(self, snapshot_type: KernelSnapshotType = KernelSnapshotType.MANUAL) -> KernelSnapshot:
        runtime = self.get_runtime()
        metrics = self.get_metrics()
        health = self._compute_product_health()
        snapshot = KernelSnapshot(
            timestamp=runtime.timestamp or "now",
            snapshot_type=snapshot_type,
            runtime=runtime,
            metrics=tuple(metrics),
            overall_health=health.overall,
        )
        self.snapshots.append(snapshot)
        return snapshot

    def get_snapshot_timeline(self) -> list[KernelSnapshot]:
        return list(self.snapshots)

    def _compute_product_health(self) -> ProductHealth:
        runtime = self.get_runtime()
        metrics = self.get_metrics()
        release = self.assess_release()

        if not metrics:
            return ProductHealth(
                overall=0.0, architecture_health=0.0, engineering_health=0.0,
                knowledge_health=0.0, capability_health=0.0, documentation_health=0.0,
            )

        avg_arch = sum(m.architecture_score for m in metrics) / len(metrics)
        avg_test = sum(m.test_score for m in metrics) / len(metrics)
        avg_docs = sum(m.documentation_score for m in metrics) / len(metrics)
        avg_cap = sum(m.runtime_maturity for m in metrics) / len(metrics)

        overall = (
            avg_arch * 0.25 +
            avg_test * 0.20 +
            avg_docs * 0.15 +
            avg_cap * 0.25 +
            release.score * 0.15
        )

        return ProductHealth(
            overall=round(overall, 1),
            architecture_health=round(avg_arch, 1),
            engineering_health=round(avg_test, 1),
            knowledge_health=round(avg_cap, 1),
            capability_health=round(avg_cap, 1),
            documentation_health=round(avg_docs, 1),
        )
