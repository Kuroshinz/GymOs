"""GymOS Kernel — Product Operating System.

The Kernel orchestrates the PRODUCT, not the workout logic.
It is the single runtime authority for product identity, capability
lifecycle, RFC lifecycle, release readiness, architecture health,
technical debt, and platform evolution.

Usage:
    from shared.kernel import kernel_runtime
    runtime = kernel_runtime.get_runtime()
    health = kernel_runtime.get_product_health()
    release = kernel_runtime.assess_release("0.5.0")
    snapshot = kernel_runtime.take_snapshot()
"""

from __future__ import annotations

from shared.kernel.kernel import (
    CapabilityTrend,
    DebtRegistryItem,
    KernelRuntime,
    KernelSnapshot,
    KernelSnapshotType,
    ProductHealth,
    ProductPhase,
    Release,
    ReleaseReadiness,
    ReleaseReadinessResult,
    RfcRecord,
    RfcStatus,
    RoadmapStage,
    RuntimeMetrics,
    TrendPoint,
)
from shared.kernel.kernel_context import (
    assess_release_readiness,
    build_kernel_runtime,
    build_runtime_metrics,
)
from shared.kernel.kernel_health import compute_product_health
from shared.kernel.kernel_history import (
    HistoryStore,
    compute_all_trends,
    compute_platform_trend,
    compute_timeline,
    compute_trend_for_capability,
)
from shared.kernel.kernel_metrics import (
    AggregatedMetrics,
    compute_aggregated_metrics,
    compute_completion_rate,
    compute_health_distribution,
    compute_maturity_distribution,
)
from shared.kernel.kernel_reports import (
    generate_capability_timeline_report,
    generate_console_summary,
    generate_debt_summary,
    generate_json_report,
    generate_markdown_report,
    generate_product_summary,
)
from shared.kernel.kernel_runtime import KernelRuntimeOrchestrator
from shared.kernel.kernel_state import KernelState, create_default_state
from shared.kernel.kernel_validator import (
    KernelValidationError,
    KernelValidationResult,
    validate_debt_item,
    validate_release,
    validate_release_readiness,
    validate_rfc,
    validate_snapshot,
)

__all__ = (
    "KernelRuntimeOrchestrator",
    "KernelState",
    "KernelRuntime",
    "KernelSnapshot",
    "RuntimeMetrics",
    "ProductHealth",
    "ReleaseReadinessResult",
    "ReleaseReadiness",
    "ProductPhase",
    "RoadmapStage",
    "RfcStatus",
    "RfcRecord",
    "Release",
    "DebtRegistryItem",
    "CapabilityTrend",
    "TrendPoint",
    "AggregatedMetrics",
    "KernelSnapshotType",
    "HistoryStore",
    "KernelValidationError",
    "KernelValidationResult",
    "create_default_state",
    "build_kernel_runtime",
    "build_runtime_metrics",
    "assess_release_readiness",
    "compute_product_health",
    "compute_aggregated_metrics",
    "compute_completion_rate",
    "compute_health_distribution",
    "compute_maturity_distribution",
    "compute_timeline",
    "compute_all_trends",
    "compute_platform_trend",
    "compute_trend_for_capability",
    "generate_markdown_report",
    "generate_json_report",
    "generate_console_summary",
    "generate_capability_timeline_report",
    "generate_debt_summary",
    "generate_product_summary",
    "validate_rfc",
    "validate_release",
    "validate_debt_item",
    "validate_snapshot",
    "validate_release_readiness",
)
