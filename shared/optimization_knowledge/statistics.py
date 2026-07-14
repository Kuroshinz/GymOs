"""Optimization Knowledge Statistics — Descriptive statistics, confidence intervals, trends, and moving averages."""

from __future__ import annotations

import math
import uuid
from datetime import datetime

from shared.optimization_knowledge.domain import (
    KnowledgeConfig,
    KnowledgeScope,
    OptimizationExperience,
    OptimizationProfile,
    OptimizationStatistics,
)


def _generate_id(prefix: str = "stat") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class StatisticsEngine:
    """Computes descriptive statistics, confidence intervals, trends, and profiles from optimization experiences."""

    def __init__(self, config: KnowledgeConfig | None = None) -> None:
        self.config = config or KnowledgeConfig()

    def compute_all(
        self,
        experiences: list[OptimizationExperience],
        scope: KnowledgeScope = KnowledgeScope.GLOBAL,
    ) -> list[OptimizationStatistics]:
        results: list[OptimizationStatistics] = []

        stats = self.compute_statistics(experiences, scope)
        results.append(stats)

        by_goal = self._group_by(experiences, lambda e: e.goal or "unknown")
        for _goal, group in by_goal.items():
            if len(group) >= self.config.min_pattern_sample:
                results.append(self.compute_statistics(
                    group, KnowledgeScope.GOAL,
                ))

        by_split = self._group_by(experiences, lambda e: e.split_style or "unknown")
        for _split, group in by_split.items():
            if len(group) >= self.config.min_pattern_sample:
                results.append(self.compute_statistics(
                    group, KnowledgeScope.SPLIT,
                ))

        return results

    def compute_statistics(
        self,
        experiences: list[OptimizationExperience],
        scope: KnowledgeScope = KnowledgeScope.GLOBAL,
    ) -> OptimizationStatistics:
        n = len(experiences)
        if n == 0:
            return OptimizationStatistics(
                statistics_id=_generate_id(), scope=scope,
                last_updated=datetime.now().isoformat(),
            )

        scores = [e.overall_score for e in experiences]
        successes = sum(1 for e in experiences if e.is_successful)

        mean = sum(scores) / n
        success_rate = successes / n
        sorted_scores = sorted(scores)
        median = sorted_scores[n // 2] if n % 2 == 1 else (
            (sorted_scores[n // 2 - 1] + sorted_scores[n // 2]) / 2
        )
        variance = sum((s - mean) ** 2 for s in scores) / n
        std_dev = math.sqrt(variance)
        ci_lower, ci_upper = self._confidence_interval(mean, std_dev, n)
        trend_direction, trend_slope = self._compute_trend(scores)
        moving_avg = self._moving_average(scores)

        return OptimizationStatistics(
            statistics_id=_generate_id(),
            scope=scope,
            total_experiences=n,
            total_successes=successes,
            total_failures=n - successes,
            success_rate=success_rate,
            mean_score=round(mean, 4),
            median_score=round(median, 4),
            std_dev_score=round(std_dev, 4),
            variance_score=round(variance, 4),
            min_score=round(min(scores), 4),
            max_score=round(max(scores), 4),
            confidence_interval_lower=round(ci_lower, 4),
            confidence_interval_upper=round(ci_upper, 4),
            trend_direction=trend_direction,
            trend_slope=round(trend_slope, 4),
            moving_average=round(moving_avg, 4),
            last_updated=datetime.now().isoformat(),
        )

    def build_profiles(
        self,
        experiences: list[OptimizationExperience],
        scope: KnowledgeScope = KnowledgeScope.GLOBAL,
    ) -> list[OptimizationProfile]:
        if not experiences:
            return []

        profiles: list[OptimizationProfile] = []

        by_goal = self._group_by(experiences, lambda e: e.goal or "unknown")
        for goal, group in by_goal.items():
            profile = self._build_single_profile(group, scope, goal)
            profiles.append(profile)

        if not profiles:
            profiles.append(self._build_single_profile(experiences, scope))

        return profiles

    def _build_single_profile(
        self,
        experiences: list[OptimizationExperience],
        scope: KnowledgeScope,
        goal: str = "",
    ) -> OptimizationProfile:
        successes = [e for e in experiences if e.is_successful]

        if not successes:
            return OptimizationProfile(
                profile_id=_generate_id(),
                scope=scope,
                total_experiences_analyzed=len(experiences),
                created_at=datetime.now().isoformat(),
            )

        best_spw = max(
            set(e.sessions_per_week for e in successes),
            key=lambda spw: sum(1 for e in successes if e.sessions_per_week == spw),
            default=0,
        )
        best_weeks = max(
            set(e.total_weeks for e in successes),
            key=lambda w: sum(1 for e in successes if e.total_weeks == w),
            default=0,
        )
        best_split = max(
            set(e.split_style for e in successes if e.split_style),
            key=lambda s: sum(1 for e in successes if e.split_style == s),
            default="",
        )
        best_avg_sets = sum(e.avg_weekly_sets for e in successes) / len(successes)
        best_meso_count = max(
            set(e.mesocycle_count for e in successes),
            key=lambda c: sum(1 for e in successes if e.mesocycle_count == c),
            default=0,
        )

        return OptimizationProfile(
            profile_id=_generate_id(),
            scope=scope,
            best_sessions_per_week=best_spw,
            best_total_weeks=best_weeks,
            best_avg_weekly_sets=round(best_avg_sets, 2),
            best_split_style=best_split,
            best_mesocycle_count=best_meso_count,
            best_goal=goal,
            avg_success_rate=round(len(successes) / len(experiences), 4),
            total_experiences_analyzed=len(experiences),
            created_at=datetime.now().isoformat(),
        )

    @staticmethod
    def _confidence_interval(
        mean: float, std_dev: float, n: int, z: float = 1.96,
    ) -> tuple[float, float]:
        if n < 2:
            return mean, mean
        margin = z * std_dev / math.sqrt(n)
        return mean - margin, mean + margin

    @staticmethod
    def _compute_trend(scores: list[float]) -> tuple[str, float]:
        n = len(scores)
        if n < 3:
            return "insufficient", 0.0
        x_vals = list(range(n))
        x_mean = (n - 1) / 2
        y_mean = sum(scores) / n
        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_vals, scores, strict=True))
        denominator = sum((x - x_mean) ** 2 for x in x_vals)
        if denominator == 0:
            return "stable", 0.0
        slope = numerator / denominator
        if slope > 0.01:
            return "up", slope
        if slope < -0.01:
            return "down", slope
        return "stable", slope

    @staticmethod
    def _moving_average(scores: list[float], window: int = 5) -> float:
        if not scores:
            return 0.0
        actual = min(window, len(scores))
        return sum(scores[-actual:]) / actual

    @staticmethod
    def _group_by(
        experiences: list[OptimizationExperience],
        key_fn,
    ) -> dict[str, list[OptimizationExperience]]:
        groups: dict[str, list[OptimizationExperience]] = {}
        for e in experiences:
            k = key_fn(e)
            if k not in groups:
                groups[k] = []
            groups[k].append(e)
        return groups
