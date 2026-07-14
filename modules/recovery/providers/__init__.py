"""Recovery Provider — abstraction for GymBrain to consume recovery data.

Design:
  - IRecoveryProvider is an interface that GymBrain consumes
  - ProductionRecoveryProvider is the SQLite-backed implementation
  - Providers are replaceable (test with MockRecoveryProvider)
  - GymBrain never accesses RecoveryRepository directly
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from modules.recovery.domain import (
    DeloadPlan,
    ReadinessAssessment,
    ReadinessLevel,
    RecoveryProfile,
    RecoveryRecommendation,
    RecoveryScore,
    RecoverySnapshot,
    RecoveryTrend,
    RecoveryTrendAnalysis,
    SleepLog,
    StressLog,
)
from modules.recovery.infrastructure.repository import RecoveryRepository


class IRecoveryProvider(ABC):
    """Abstract interface for recovery data access.

    GymBrain consumes recovery data exclusively through this interface.
    Never couples GymBrain to a specific repository or database.
    """

    @abstractmethod
    def get_today_score(self) -> RecoveryScore | None:
        ...

    @abstractmethod
    def get_score_by_date(self, date: str) -> RecoveryScore | None:
        ...

    @abstractmethod
    def get_recent_scores(self, days: int = 7) -> list[RecoveryScore]:
        ...

    @abstractmethod
    def get_latest_sleep(self) -> SleepLog | None:
        ...

    @abstractmethod
    def get_sleep_by_date(self, date: str) -> SleepLog | None:
        ...

    @abstractmethod
    def get_recent_sleep(self, days: int = 7) -> list[SleepLog]:
        ...

    @abstractmethod
    def get_latest_stress(self) -> StressLog | None:
        ...

    @abstractmethod
    def get_recent_stress(self, days: int = 7) -> list[StressLog]:
        ...

    @abstractmethod
    def get_readiness(self) -> ReadinessAssessment | None:
        ...

    @abstractmethod
    def get_recent_readiness(self, days: int = 7) -> list[ReadinessAssessment]:
        ...

    @abstractmethod
    def get_active_deload(self) -> DeloadPlan | None:
        ...

    @abstractmethod
    def get_recent_deloads(self, limit: int = 5) -> list[DeloadPlan]:
        ...

    @abstractmethod
    def get_profile(self) -> RecoveryProfile:
        ...

    @abstractmethod
    def get_recent_recommendations(self, days: int = 7) -> list[RecoveryRecommendation]:
        ...

    @abstractmethod
    def has_data(self) -> bool:
        ...

    @abstractmethod
    def get_average_score(self, days: int = 7) -> float:
        ...

    @abstractmethod
    def get_snapshot(self) -> RecoverySnapshot:
        ...

    @abstractmethod
    def get_trend(self, days: int = 14) -> RecoveryTrend:
        ...


class ProductionRecoveryProvider(IRecoveryProvider):
    """SQLite-backed RecoveryProvider for production use.

    Wraps RecoveryRepository and provides recovery data to GymBrain.
    """

    def __init__(self, repository: RecoveryRepository, db: Any = None) -> None:
        self._repo = repository
        self._db = db

    def get_today_score(self) -> RecoveryScore | None:
        today = datetime.now().strftime("%Y-%m-%d")
        return self._repo.get_score_by_date(today)

    def get_score_by_date(self, date: str) -> RecoveryScore | None:
        return self._repo.get_score_by_date(date)

    def get_recent_scores(self, days: int = 7) -> list[RecoveryScore]:
        return self._repo.list_scores(days=days)

    def get_latest_sleep(self) -> SleepLog | None:
        logs = self._repo.list_sleep_logs(days=7)
        return logs[0] if logs else None

    def get_sleep_by_date(self, date: str) -> SleepLog | None:
        return self._repo.get_sleep_by_date(date)

    def get_recent_sleep(self, days: int = 7) -> list[SleepLog]:
        return self._repo.list_sleep_logs(days=days)

    def get_latest_stress(self) -> StressLog | None:
        logs = self._repo.list_stress_logs(days=7)
        return logs[0] if logs else None

    def get_recent_stress(self, days: int = 7) -> list[StressLog]:
        return self._repo.list_stress_logs(days=days)

    def get_readiness(self) -> ReadinessAssessment | None:
        today = datetime.now().strftime("%Y-%m-%d")
        return self._repo.get_readiness_by_date(today)

    def get_recent_readiness(self, days: int = 7) -> list[ReadinessAssessment]:
        return self._repo.list_readiness(days=days)

    def get_active_deload(self) -> DeloadPlan | None:
        return self._repo.get_active_deload_plan()

    def get_recent_deloads(self, limit: int = 5) -> list[DeloadPlan]:
        return self._repo.list_deload_plans(limit=limit)

    def get_profile(self) -> RecoveryProfile:
        profile = self._repo.get_profile()
        if profile is None:
            profile = RecoveryProfile()
            self._repo.save_profile(profile)
        return profile

    def get_recent_recommendations(self, days: int = 7) -> list[RecoveryRecommendation]:
        return self._repo.list_recommendations(days=days)

    def has_data(self) -> bool:
        return self._repo.has_data()

    def get_average_score(self, days: int = 7) -> float:
        return self._repo.get_average_score(days=days)

    def get_snapshot(self) -> RecoverySnapshot:
        """Build a complete recovery snapshot for the Dashboard."""
        today = datetime.now().strftime("%Y-%m-%d")
        score = self.get_today_score()
        trend = self.get_trend(days=14)
        active_deload = self.get_active_deload()
        recs = self.get_recent_recommendations(days=3)

        flags: list[str] = []
        if active_deload:
            flags.append(f"Deload in progress (until {active_deload.end_date})")
        if trend.direction.value == "declining":
            flags.append("Recovery trend is declining")
        if trend.direction.value == "volatile":
            flags.append("Recovery is unstable")

        return RecoverySnapshot(
            date=today,
            recovery_score=score.overall_score if score else 0.0,
            readiness_score=score.readiness_score if score else 0.0,
            readiness_level=score.readiness_level if score else ReadinessLevel.GOOD,
            fatigue_score=score.fatigue_score if score else 0.0,
            sleep_score=score.sleep_score if score else 0.0,
            stress_score=score.stress_score if score else 0.0,
            trend=trend.direction,
            flags=flags,
            recommendations=[r.message for r in recs[:3]],
        )

    def get_trend(self, days: int = 14) -> RecoveryTrendAnalysis:
        """Calculate recovery trend from recent scores."""
        scores = self._repo.list_scores(days=days)
        if len(scores) < 3:
            return RecoveryTrendAnalysis(direction=RecoveryTrend.STABLE, days_analyzed=len(scores))

        scores_sorted = sorted(scores, key=lambda s: s.date)
        values = [s.overall_score for s in scores_sorted]
        dates = [s.date for s in scores_sorted]

        avg = sum(values) / len(values)
        mn = min(values)
        mx = max(values)
        variance = sum((v - avg) ** 2 for v in values) / len(values)
        std_dev = variance ** 0.5

        # Simple linear regression slope
        n = len(values)
        x_mean = (n - 1) / 2.0
        y_mean = avg
        num = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
        den = sum((i - x_mean) ** 2 for i in range(n))
        slope = num / den if den else 0.0

        # Weekly averages
        weekly_avgs: list[float] = []
        for i in range(0, n, 7):
            chunk = values[i:i + 7]
            weekly_avgs.append(sum(chunk) / len(chunk))

        # Determine direction
        cv = std_dev / avg if avg > 0 else 0.0
        if cv > 0.25:
            direction = RecoveryTrend.VOLATILE
        elif slope > 0.5:
            direction = RecoveryTrend.IMPROVING
        elif slope < -0.5:
            direction = RecoveryTrend.DECLINING
        else:
            direction = RecoveryTrend.STABLE

        return RecoveryTrendAnalysis(
            direction=direction,
            average_score=round(avg, 1),
            min_score=round(mn, 1),
            max_score=round(mx, 1),
            std_dev=round(std_dev, 1),
            slope=round(slope, 2),
            days_analyzed=n,
            recent_scores=values,
            recent_dates=dates,
            weekly_averages=weekly_avgs,
            explanation=f"{direction.value.title()} trend (slope: {slope:+.2f}/day, CV: {cv:.2f})",
        )
