"""Technical debt model — individual debt items and aggregated view."""

from __future__ import annotations

from dataclasses import dataclass, field

from shared.capabilities.enums import DebtSeverity


@dataclass(frozen=True)
class TechnicalDebtItem:
    """A single identified technical debt item."""
    debt_id: str
    description: str
    severity: DebtSeverity
    capability_id: str
    owner: str = ""
    planned_version: str = ""
    status: str = "identified"  # identified, in_progress, resolved, accepted
    created_at: str = ""
    resolved_at: str = ""
    notes: str = ""

    @property
    def is_resolved(self) -> bool:
        return self.status == "resolved"

    @property
    def is_blocking(self) -> bool:
        return self.severity in (DebtSeverity.HIGH, DebtSeverity.CRITICAL) and not self.is_resolved


@dataclass(frozen=True)
class TechnicalDebtSummary:
    """Aggregated technical debt view for a capability or platform."""
    total_items: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    resolved: int = 0
    items: tuple[TechnicalDebtItem, ...] = field(default_factory=tuple)

    @property
    def blocking_count(self) -> int:
        return sum(1 for item in self.items if item.is_blocking)

    @property
    def unresolved_count(self) -> int:
        return self.total_items - self.resolved

    @property
    def debt_ratio(self) -> float:
        if self.total_items == 0:
            return 0.0
        return self.unresolved_count / self.total_items
