"""Optimization Knowledge Pattern Mining — Extracts volume, frequency, split, recovery, adherence, deload, and fatigue patterns from experiences."""

from __future__ import annotations

import uuid
from datetime import datetime

from shared.optimization_knowledge.domain import (
    KnowledgeConfig,
    KnowledgeScope,
    OptimizationExperience,
    OptimizationPattern,
    PatternType,
)


def _generate_id(prefix: str = "pat") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class PatternMiningEngine:
    """Mines patterns from optimization experiences across 7 dimensions.

    Each pattern represents a range of values for a parameter and its associated
    success rate, sample size, and confidence level.
    """

    def __init__(self, config: KnowledgeConfig | None = None) -> None:
        self.config = config or KnowledgeConfig()

    def mine_all(
        self,
        experiences: list[OptimizationExperience],
        scope: KnowledgeScope = KnowledgeScope.GLOBAL,
    ) -> list[OptimizationPattern]:
        patterns: list[OptimizationPattern] = []
        miners = [
            self._mine_volume_patterns,
            self._mine_frequency_patterns,
            self._mine_split_patterns,
            self._mine_recovery_patterns,
            self._mine_adherence_patterns,
            self._mine_deload_patterns,
            self._mine_fatigue_patterns,
        ]
        for miner in miners:
            result = miner(experiences, scope)
            patterns.extend(result)
        return patterns

    def _mine_volume_patterns(
        self,
        experiences: list[OptimizationExperience],
        scope: KnowledgeScope,
    ) -> list[OptimizationPattern]:
        return self._build_range_patterns(
            experiences, PatternType.VOLUME, "Average Weekly Sets",
            [e.avg_weekly_sets for e in experiences],
            list(range(10, 201, 20)),
            scope,
        )

    def _mine_frequency_patterns(
        self,
        experiences: list[OptimizationExperience],
        scope: KnowledgeScope,
    ) -> list[OptimizationPattern]:
        return self._build_discrete_patterns(
            experiences, PatternType.FREQUENCY, "Sessions Per Week",
            [e.sessions_per_week for e in experiences],
            sorted(set(e.sessions_per_week for e in experiences if e.sessions_per_week > 0)),
            scope,
        )

    def _mine_split_patterns(
        self,
        experiences: list[OptimizationExperience],
        scope: KnowledgeScope,
    ) -> list[OptimizationPattern]:
        return self._build_categorical_patterns(
            experiences, PatternType.SPLIT, "Split Style",
            [e.split_style for e in experiences if e.split_style],
            scope,
        )

    def _mine_recovery_patterns(
        self,
        experiences: list[OptimizationExperience],
        scope: KnowledgeScope,
    ) -> list[OptimizationPattern]:
        return self._build_range_patterns(
            experiences, PatternType.RECOVERY, "Total Weeks",
            [float(e.total_weeks) for e in experiences],
            list(range(4, 53, 4)),
            scope,
        )

    def _mine_adherence_patterns(
        self,
        experiences: list[OptimizationExperience],
        scope: KnowledgeScope,
    ) -> list[OptimizationPattern]:
        return self._build_range_patterns(
            experiences, PatternType.ADHERENCE, "Mesocycle Count",
            [float(e.mesocycle_count) for e in experiences],
            list(range(1, 11)),
            scope,
        )

    def _mine_deload_patterns(
        self,
        experiences: list[OptimizationExperience],
        scope: KnowledgeScope,
    ) -> list[OptimizationPattern]:
        with_deload = [e for e in experiences if e.has_deload]
        without_deload = [e for e in experiences if not e.has_deload]
        patterns: list[OptimizationPattern] = []

        if with_deload:
            sr = self._success_rate(with_deload)
            patterns.append(OptimizationPattern(
                pattern_id=_generate_id(),
                pattern_type=PatternType.DELOAD,
                label="With Deload Weeks",
                description="Plans that include deload weeks",
                value_range_min=1.0,
                value_range_max=1.0,
                value_range_mean=1.0,
                success_rate=sr,
                sample_size=len(with_deload),
                confidence=self._compute_confidence(len(with_deload), sr),
                scope=scope,
                tags=["deload", "included"],
                created_at=datetime.now().isoformat(),
            ))
        if without_deload:
            sr = self._success_rate(without_deload)
            patterns.append(OptimizationPattern(
                pattern_id=_generate_id(),
                pattern_type=PatternType.DELOAD,
                label="Without Deload Weeks",
                description="Plans that do not include deload weeks",
                value_range_min=0.0,
                value_range_max=0.0,
                value_range_mean=0.0,
                success_rate=sr,
                sample_size=len(without_deload),
                confidence=self._compute_confidence(len(without_deload), sr),
                scope=scope,
                tags=["deload", "excluded"],
                created_at=datetime.now().isoformat(),
            ))
        return patterns

    def _mine_fatigue_patterns(
        self,
        experiences: list[OptimizationExperience],
        scope: KnowledgeScope,
    ) -> list[OptimizationPattern]:
        return self._build_range_patterns(
            experiences, PatternType.FATIGUE, "Total Sets",
            [float(e.total_sets) for e in experiences],
            list(range(0, 3001, 200)),
            scope,
        )

    def _build_range_patterns(
        self,
        experiences: list[OptimizationExperience],
        pattern_type: PatternType,
        label_prefix: str,
        values: list[float],
        bins: list[int],
        scope: KnowledgeScope,
    ) -> list[OptimizationPattern]:
        patterns: list[OptimizationPattern] = []
        for i in range(len(bins) - 1):
            lo, hi = bins[i], bins[i + 1]
            in_range = [
                (e, v) for e, v in zip(experiences, values, strict=True)
                if lo <= v < hi
            ]
            if len(in_range) < self.config.min_pattern_sample:
                continue
            group_exps = [e for e, _ in in_range]
            sr = self._success_rate(group_exps)
            mean_val = sum(v for _, v in in_range) / len(in_range)
            pattern = OptimizationPattern(
                pattern_id=_generate_id(),
                pattern_type=pattern_type,
                label=f"{label_prefix} [{lo}-{hi}]",
                description=f"Average weekly sets between {lo} and {hi}",
                value_range_min=float(lo),
                value_range_max=float(hi),
                value_range_mean=mean_val,
                success_rate=sr,
                sample_size=len(in_range),
                confidence=self._compute_confidence(len(in_range), sr),
                scope=scope,
                created_at=datetime.now().isoformat(),
            )
            patterns.append(pattern)
        return patterns

    def _build_discrete_patterns(
        self,
        experiences: list[OptimizationExperience],
        pattern_type: PatternType,
        label_prefix: str,
        values: list[int],
        unique_values: list[int],
        scope: KnowledgeScope,
    ) -> list[OptimizationPattern]:
        patterns: list[OptimizationPattern] = []
        for val in unique_values:
            group = [e for e, v in zip(experiences, values, strict=True) if v == val]
            if len(group) < self.config.min_pattern_sample:
                continue
            sr = self._success_rate(group)
            pattern = OptimizationPattern(
                pattern_id=_generate_id(),
                pattern_type=pattern_type,
                label=f"{label_prefix}: {val}",
                description=f"Plans with {val} sessions per week",
                value_range_min=float(val),
                value_range_max=float(val),
                value_range_mean=float(val),
                success_rate=sr,
                sample_size=len(group),
                confidence=self._compute_confidence(len(group), sr),
                scope=scope,
                created_at=datetime.now().isoformat(),
            )
            patterns.append(pattern)
        return patterns

    def _build_categorical_patterns(
        self,
        experiences: list[OptimizationExperience],
        pattern_type: PatternType,
        label_prefix: str,
        values: list[str],
        scope: KnowledgeScope,
    ) -> list[OptimizationPattern]:
        patterns: list[OptimizationPattern] = []
        categories = sorted(set(values))
        for cat in categories:
            group = [e for e, v in zip(experiences, values, strict=True) if v == cat]
            if len(group) < self.config.min_pattern_sample:
                continue
            sr = self._success_rate(group)
            pattern = OptimizationPattern(
                pattern_id=_generate_id(),
                pattern_type=pattern_type,
                label=f"{label_prefix}: {cat.title()}",
                description=f"Plans using {cat} split style",
                value_range_min=0.0,
                value_range_max=0.0,
                value_range_mean=0.0,
                success_rate=sr,
                sample_size=len(group),
                confidence=self._compute_confidence(len(group), sr),
                scope=scope,
                tags=[cat],
                created_at=datetime.now().isoformat(),
            )
            patterns.append(pattern)
        return patterns

    @staticmethod
    def _success_rate(experiences: list[OptimizationExperience]) -> float:
        if not experiences:
            return 0.0
        return sum(1 for e in experiences if e.is_successful) / len(experiences)

    @staticmethod
    def _compute_confidence(sample_size: int, success_rate: float) -> float:
        if sample_size < 5:
            return 0.0
        base = min(1.0, sample_size / 100)
        variance = success_rate * (1 - success_rate) / max(sample_size, 1)
        std_err = variance ** 0.5
        confidence = base * (1.0 - std_err)
        return max(0.0, min(1.0, confidence))
