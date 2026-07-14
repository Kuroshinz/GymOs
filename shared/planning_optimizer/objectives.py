"""Planning Optimizer Objectives — Pure scoring functions for each optimization objective."""

from __future__ import annotations

import math
from typing import Any

from shared.planning_optimizer.domain import ObjectiveType, OptimizationObjective


class ObjectiveScorer:
    """Pure functions that compute objective scores from plan data.

    Each method returns a score in [0.0, 1.0] where 1.0 is optimal.
    All methods are deterministic — no randomness, no external state.
    """

    @staticmethod
    def score_hypertrophy(plan_data: dict[str, Any]) -> float:
        """Score how well a plan maximizes hypertrophy stimulus."""
        total_sets = plan_data.get("total_sets") or 0
        total_sessions = plan_data.get("total_sessions") or 0
        mesocycles = plan_data.get("mesocycles", []) or []

        if total_sessions == 0:
            return 0.0

        volume_score = min(1.0, total_sets / (total_sessions * 40))

        meso_count = max(len(mesocycles), 1)
        hypertrophy_meso_ratio = sum(
            1 for m in mesocycles
            if m.get("goal", "").lower() in ("hypertrophy", "maximize_hypertrophy")
        ) / meso_count

        progression_penalty = 0.0
        for m in mesocycles:
            weeks = m.get("week_count", 4)
            if weeks < 3:
                progression_penalty += 0.1

        score = (volume_score * 0.4) + (hypertrophy_meso_ratio * 0.4) - progression_penalty
        return max(0.0, min(1.0, score))

    @staticmethod
    def score_fatigue(plan_data: dict[str, Any]) -> float:
        """Score how well a plan minimizes fatigue burden (higher = less fatigue)."""
        total_sets = plan_data.get("total_sets", 0)
        total_weeks = plan_data.get("total_weeks", 1)
        weeks = plan_data.get("weeks", [])

        if total_weeks == 0:
            return 0.0

        avg_weekly_sets = total_sets / total_weeks
        volume_penalty = max(0.0, (avg_weekly_sets - 80) / 160)
        volume_score = 1.0 - volume_penalty

        weeks_with_rest = sum(1 for w in weeks if w.get("has_rest_days", False))
        rest_ratio = weeks_with_rest / max(len(weeks), 1)
        rest_score = rest_ratio * 0.5 + 0.5

        deload_weeks = sum(1 for w in weeks if w.get("is_deload_week", False))
        deload_ratio = deload_weeks / max(len(weeks), 1)
        deload_score = min(1.0, deload_ratio * 10)

        return max(0.0, min(1.0, (volume_score * 0.5) + (rest_score * 0.3) + (deload_score * 0.2)))

    @staticmethod
    def score_recovery(plan_data: dict[str, Any]) -> float:
        """Score how well a plan enables recovery."""
        weeks = plan_data.get("weeks", [])
        if not weeks:
            return 0.0

        rest_days = sum(1 for w in weeks for s in w.get("sessions", []) if s.get("day_type") == "rest")
        all_sessions = sum(len(w.get("sessions", [])) for w in weeks)

        if all_sessions == 0:
            return 0.5

        rest_ratio = rest_days / max(all_sessions, 1)
        rest_score = min(1.0, rest_ratio * 3)

        deload_weeks = sum(1 for w in weeks if w.get("is_deload_week", False))
        total_weeks = max(len(weeks), 1)
        deload_score = min(1.0, (deload_weeks / total_weeks) * 15)

        max_consecutive = 0
        for w in weeks:
            current_run = 0
            for s in w.get("sessions", []):
                if s.get("day_type") != "rest":
                    current_run += 1
                    max_consecutive = max(max_consecutive, current_run)
                else:
                    current_run = 0

        consecutive_penalty = max(0.0, (max_consecutive - 5) / 5)

        return max(0.0, min(1.0, (rest_score * 0.4) + (deload_score * 0.3) - consecutive_penalty * 0.3))

    @staticmethod
    def score_adherence(plan_data: dict[str, Any]) -> float:
        """Score how likely a plan is to be adhered to."""
        sessions_per_week = plan_data.get("sessions_per_week") or plan_data.get("sessions_per_week_default", 5)
        total_weeks = plan_data.get("total_weeks", 1)
        mesocycles = plan_data.get("mesocycles", []) or []

        frequency_penalty = max(0.0, (sessions_per_week - 6) / 4)
        frequency_score = 1.0 - frequency_penalty

        consistency_bonus = 0.0
        for m in mesocycles:
            weeks = m.get("week_count", 4)
            if 3 <= weeks <= 6:
                consistency_bonus += 0.05

        duration_penalty = min(0.3, (total_weeks - 16) * 0.02) if total_weeks > 16 else 0.0

        score = frequency_score + consistency_bonus - duration_penalty
        return max(0.0, min(1.0, score))

    @staticmethod
    def score_plateau_risk(plan_data: dict[str, Any]) -> float:
        """Score how well a plan minimizes plateau risk (higher = lower risk)."""
        mesocycles = plan_data.get("mesocycles", [])
        if not mesocycles:
            return 0.5

        goals = [m.get("goal", "") for m in mesocycles]
        unique_goals = set(g for g in goals if g)

        variety_bonus = min(1.0, len(unique_goals) / 3)
        variety_score = variety_bonus * 0.4

        progression_score = 0.0
        for m in mesocycles:
            weeks = m.get("week_count", 4)
            if 4 <= weeks <= 6:
                progression_score += 0.1

        has_deload = any(m.get("has_deload", False) for m in mesocycles)
        deload_bonus = 0.2 if has_deload else 0.0

        score = variety_score + min(1.0, progression_score) * 0.4 + deload_bonus
        return max(0.0, min(1.0, score))

    @staticmethod
    def score_injury_risk(plan_data: dict[str, Any]) -> float:
        """Score how well a plan minimizes injury risk (higher = lower risk)."""
        total_sets = plan_data.get("total_sets", 0)
        total_weeks = plan_data.get("total_weeks", 1)
        weeks = plan_data.get("weeks", [])

        if total_weeks == 0:
            return 0.5

        avg_weekly_sets = total_sets / total_weeks
        volume_penalty = min(0.5, (avg_weekly_sets - 120) / 80) if avg_weekly_sets > 120 else 0.0

        deload_weeks = sum(1 for w in weeks if w.get("is_deload_week", False))
        deload_ratio = deload_weeks / total_weeks

        if deload_ratio >= 0.1:
            deload_score = 1.0
        elif deload_ratio >= 0.05:
            deload_score = 0.7
        else:
            deload_score = 0.3

        high_volume_sessions = 0
        total_sessions_count = 0
        for w in weeks:
            for s in w.get("sessions", []):
                total_sessions_count += 1
                s_sets = sum(e.get("sets", 0) for e in s.get("exercises", []))
                if s_sets > 15:
                    high_volume_sessions += 1

        if total_sessions_count > 0:
            spike_penalty = min(0.3, high_volume_sessions / total_sessions_count)
        else:
            spike_penalty = 0.0

        score = 1.0 - volume_penalty + deload_score * 0.2 - spike_penalty
        return max(0.0, min(1.0, score))

    @staticmethod
    def score_strength(plan_data: dict[str, Any]) -> float:
        """Score how well a plan maximizes strength development."""
        mesocycles = plan_data.get("mesocycles", [])
        if not mesocycles:
            return 0.0

        strength_meso_ratio = sum(
            1 for m in mesocycles
            if m.get("goal", "").lower() in ("strength", "max_strength", "maximize_strength")
        ) / max(len(mesocycles), 1)

        low_rep_count = 0
        total_exercises = 0
        for m in mesocycles:
            for w in m.get("weeks", []):
                for s in w.get("sessions", []):
                    for e in s.get("exercises", []):
                        total_exercises += 1
                        if e.get("reps", 8) <= 5:
                            low_rep_count += 1

        if total_exercises > 0:
            intensity_score = min(1.0, low_rep_count / total_exercises * 2)
        else:
            intensity_score = 0.0

        return max(0.0, min(1.0, strength_meso_ratio * 0.6 + intensity_score * 0.4))

    @staticmethod
    def score_endurance(plan_data: dict[str, Any]) -> float:
        """Score how well a plan maximizes muscular endurance."""
        mesocycles = plan_data.get("mesocycles", [])
        if not mesocycles:
            return 0.0

        endurance_meso_ratio = sum(
            1 for m in mesocycles
            if m.get("goal", "").lower() in ("endurance", "conditioning", "maximize_endurance")
        ) / max(len(mesocycles), 1)

        high_rep_count = 0
        total_exercises = 0
        for m in mesocycles:
            for w in m.get("weeks", []):
                for s in w.get("sessions", []):
                    for e in s.get("exercises", []):
                        total_exercises += 1
                        if e.get("reps", 8) >= 15:
                            high_rep_count += 1

        if total_exercises > 0:
            endurance_score = min(1.0, high_rep_count / total_exercises * 2)
        else:
            endurance_score = 0.0

        return max(0.0, min(1.0, endurance_meso_ratio * 0.5 + endurance_score * 0.5))

    @staticmethod
    def score_volume_balance(plan_data: dict[str, Any]) -> float:
        """Score how evenly volume is distributed across the plan."""
        weeks = plan_data.get("weeks", [])
        if len(weeks) < 2:
            return 0.5

        weekly_volumes = []
        for w in weeks:
            vol = sum(
                e.get("sets", 0)
                for s in w.get("sessions", [])
                for e in s.get("exercises", [])
            )
            weekly_volumes.append(vol)

        if not weekly_volumes or max(weekly_volumes) == 0:
            return 0.5

        mean_vol = sum(weekly_volumes) / len(weekly_volumes)
        variance = sum((v - mean_vol) ** 2 for v in weekly_volumes) / len(weekly_volumes)
        std_dev = math.sqrt(variance)

        cv = std_dev / mean_vol if mean_vol > 0 else 0
        balance_score = 1.0 - min(1.0, cv)

        return max(0.0, min(1.0, balance_score))

    @staticmethod
    def score_progression_quality(plan_data: dict[str, Any]) -> float:
        """Score how well the plan progresses over time."""
        weeks = plan_data.get("weeks", [])
        if len(weeks) < 2:
            return 0.5

        weekly_volumes = []
        for w in weeks:
            vol = sum(
                e.get("sets", 0)
                for s in w.get("sessions", [])
                for e in s.get("exercises", [])
            )
            weekly_volumes.append(vol)

        if all(v == 0 for v in weekly_volumes):
            return 0.0

        progression_count = sum(
            1 for i in range(1, len(weekly_volumes))
            if weekly_volumes[i] > weekly_volumes[i - 1]
        )
        regression_count = sum(
            1 for i in range(1, len(weekly_volumes))
            if weekly_volumes[i] < weekly_volumes[i - 1]
        )

        progression_ratio = progression_count / max(len(weekly_volumes) - 1, 1)
        regression_penalty = regression_count / max(len(weekly_volumes) - 1, 1)

        score = progression_ratio * 0.7 - regression_penalty * 0.3
        return max(0.0, min(1.0, score))

    @staticmethod
    def compute_objective_score(
        objective: OptimizationObjective,
        plan_data: dict[str, Any],
    ) -> float:
        """Dispatch to the correct scorer based on objective type."""
        dispatcher = {
            ObjectiveType.MAXIMIZE_HYPERTROPHY: ObjectiveScorer.score_hypertrophy,
            ObjectiveType.MINIMIZE_FATIGUE: ObjectiveScorer.score_fatigue,
            ObjectiveType.MAXIMIZE_RECOVERY: ObjectiveScorer.score_recovery,
            ObjectiveType.MAXIMIZE_ADHERENCE: ObjectiveScorer.score_adherence,
            ObjectiveType.MINIMIZE_PLATEAU_RISK: ObjectiveScorer.score_plateau_risk,
            ObjectiveType.MINIMIZE_INJURY_RISK: ObjectiveScorer.score_injury_risk,
            ObjectiveType.MAXIMIZE_STRENGTH: ObjectiveScorer.score_strength,
            ObjectiveType.MAXIMIZE_ENDURANCE: ObjectiveScorer.score_endurance,
            ObjectiveType.BALANCE_VOLUME: ObjectiveScorer.score_volume_balance,
            ObjectiveType.MAXIMIZE_PROGRESSION: ObjectiveScorer.score_progression_quality,
        }
        scorer = dispatcher.get(objective.objective_type)
        if scorer is None:
            return 0.0
        return scorer(plan_data)

    @staticmethod
    def compute_weighted_score(
        objectives: list[OptimizationObjective],
        plan_data: dict[str, Any],
    ) -> float:
        """Compute weighted sum across all objectives."""
        if not objectives:
            return 0.0
        total_weight = sum(o.weight for o in objectives)
        if total_weight == 0:
            return 0.0
        weighted = sum(
            ObjectiveScorer.compute_objective_score(o, plan_data) * o.weight
            for o in objectives
        )
        return weighted / total_weight
