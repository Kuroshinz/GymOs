"""Capability metrics — typed scores and measurement results."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class MetricResult:
    """A single measured metric with label, score, and target."""
    label: str
    score: float
    target: float
    unit: str = "percent"

    @property
    def percentage(self) -> float:
        if self.target == 0.0:
            return 0.0
        return min((self.score / self.target) * 100.0, 100.0)

    @property
    def is_met(self) -> bool:
        return self.score >= self.target


@dataclass(frozen=True)
class HealthScore:
    """Composite health score with sub-scores."""
    overall: float
    architecture: float = 0.0
    test_coverage: float = 0.0
    documentation: float = 0.0
    platform: float = 0.0
    sub_scores: tuple[MetricResult, ...] = field(default_factory=tuple)

    @property
    def is_healthy(self) -> bool:
        return self.overall >= 70.0

    @property
    def rating(self) -> str:
        if self.overall >= 90.0:
            return "excellent"
        if self.overall >= 70.0:
            return "good"
        if self.overall >= 50.0:
            return "fair"
        if self.overall >= 30.0:
            return "poor"
        return "critical"


@dataclass(frozen=True)
class CompletionMetrics:
    """Completion metrics for a capability."""
    current_percent: float
    target_percent: float
    remaining_tasks: int = 0
    total_tasks: int = 0

    @property
    def is_complete(self) -> bool:
        return self.current_percent >= self.target_percent

    @property
    def progress_label(self) -> str:
        return f"{self.current_percent:.0f}% / {self.target_percent:.0f}%"
