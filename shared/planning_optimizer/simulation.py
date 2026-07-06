"""Planning Optimizer Simulation — Simulation pipeline that evaluates a candidate through prediction, recovery, nutrition, and decision engines."""

from __future__ import annotations

import json
import uuid
from typing import Any

from shared.planning_optimizer.constraints import ConstraintChecker
from shared.planning_optimizer.domain import (
    CandidateStatus,
    OptimizationCandidate,
    OptimizationConstraint,
    OptimizationObjective,
    OptimizationResult,
    OptimizationScore,
    OptimizerStatus,
)
from shared.planning_optimizer.scoring import CompositeScorer


def _generate_id(prefix: str = "sim") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


class SimulationPipeline:
    """Simulates a candidate plan through the evaluation pipeline.

    Each stage is a pure function — no side effects, no I/O.
    The pipeline mirrors the real GymOS architecture:
      Candidate → Prediction → Recovery → Nutrition → Decision → Score
    """

    def __init__(self) -> None:
        self._simulated_predictions: dict[str, Any] = {}
        self._simulated_recovery: dict[str, Any] = {}
        self._simulated_nutrition: dict[str, Any] = {}

    def run(
        self,
        plan_data: dict[str, Any],
        objectives: list[OptimizationObjective],
        constraints: list[OptimizationConstraint],
        candidate_id: str = "",
    ) -> OptimizationCandidate:
        """Run the full simulation pipeline on a candidate plan."""
        cid = candidate_id or _generate_id("candidate")
        macro = plan_data

        prediction = self._simulate_prediction(macro)
        macro["prediction"] = prediction

        recovery = self._simulate_recovery(macro)
        macro["recovery"] = recovery

        nutrition = self._simulate_nutrition(macro)
        macro["nutrition"] = nutrition

        decision = self._simulate_decision(macro)
        macro["decision"] = decision

        scores = self._compute_scores(macro, objectives, constraints)

        _, violations, _ = ConstraintChecker.check_all(macro, constraints)
        is_feasible = len(violations) == 0

        return OptimizationCandidate(
            candidate_id=cid,
            macrocycle_json=json.dumps(macro),
            scores=scores,
            mutations=[],
            generation=0,
            rank=0,
            status=CandidateStatus.ACTIVE if is_feasible else CandidateStatus.INFEASIBLE,
            constraint_violations=violations,
            is_feasible=is_feasible,
        )

    def run_many(
        self,
        plans: list[dict[str, Any]],
        objectives: list[OptimizationObjective],
        constraints: list[OptimizationConstraint],
        start_generation: int = 0,
    ) -> list[OptimizationCandidate]:
        return [
            self.run(p, objectives, constraints)
            for p in plans
        ]

    def _simulate_prediction(self, plan_data: dict[str, Any]) -> dict[str, Any]:
        """Simulate the Prediction Engine output.

        Estimates expected progress, volume response, and adaptation window.
        """
        total_sets = plan_data.get("total_sets", 0)
        total_weeks = max(plan_data.get("total_weeks", 1), 1)
        weeks = plan_data.get("weeks", [])

        avg_weekly_sets = total_sets / total_weeks

        estimated_hypertrophy = min(1.0, avg_weekly_sets / 80) * 0.7
        estimated_strength = min(1.0, avg_weekly_sets / 60) * 0.5
        estimated_endurance = min(1.0, avg_weekly_sets / 100) * 0.3

        adaptation_window = 4 + int(total_weeks * 0.15)

        deload_weeks = sum(1 for w in weeks if w.get("is_deload_week", False))
        plateau_risk = max(0.0, 1.0 - (deload_weeks / max(total_weeks, 1)) * 10)

        return {
            "estimated_hypertrophy_gain": round(estimated_hypertrophy, 3),
            "estimated_strength_gain": round(estimated_strength, 3),
            "estimated_endurance_gain": round(estimated_endurance, 3),
            "adaptation_window_weeks": adaptation_window,
            "expected_plateau_week": int(total_weeks * 0.7),
            "volume_response_score": round(min(1.0, avg_weekly_sets / 60), 3),
            "plateau_risk": round(plateau_risk, 3),
        }

    def _simulate_recovery(self, plan_data: dict[str, Any]) -> dict[str, Any]:
        """Simulate the Recovery Engine output.

        Estimates recovery demand, fatigue accumulation, and rest adequacy.
        """
        total_sets = plan_data.get("total_sets", 0)
        total_weeks = max(plan_data.get("total_weeks", 1), 1)
        weeks = plan_data.get("weeks", [])

        avg_weekly_sets = total_sets / total_weeks

        fatigue_score = max(0.0, 1.0 - avg_weekly_sets / 150)
        recovery_demand = min(1.0, avg_weekly_sets / 100)

        rest_sessions = sum(
            1 for w in weeks for s in w.get("sessions", [])
            if s.get("day_type") == "rest"
        )
        total_sessions_count = sum(len(w.get("sessions", [])) for w in weeks)
        rest_adequacy = rest_sessions / max(total_sessions_count, 1)

        deload_weeks = sum(1 for w in weeks if w.get("is_deload_week", False))
        deload_adequacy = min(1.0, deload_weeks / max(total_weeks * 0.08, 1))

        return {
            "fatigue_score": round(fatigue_score, 3),
            "recovery_demand": round(recovery_demand, 3),
            "rest_adequacy": round(rest_adequacy, 3),
            "deload_adequacy": round(deload_adequacy, 3),
            "hrv_impact": round(max(0.0, 1.0 - recovery_demand * 0.5), 3),
            "sleep_quality_impact": round(max(0.0, 1.0 - avg_weekly_sets / 200), 3),
        }

    def _simulate_nutrition(self, plan_data: dict[str, Any]) -> dict[str, Any]:
        """Simulate the Nutrition Engine output.

        Estimates caloric and macro requirements for the plan.
        """
        total_sets = plan_data.get("total_sets", 0)
        total_weeks = max(plan_data.get("total_weeks", 1), 1)
        avg_weekly_sets = total_sets / total_weeks

        base_calories = 2200
        activity_multiplier = 1.0 + avg_weekly_sets / 300
        estimated_calories = int(base_calories * activity_multiplier)
        estimated_protein = int(1.8 * 80)
        estimated_carbs = int(estimated_calories * 0.45 / 4)
        estimated_fat = int(estimated_calories * 0.25 / 9)

        return {
            "estimated_daily_calories": estimated_calories,
            "estimated_daily_protein_g": estimated_protein,
            "estimated_daily_carbs_g": estimated_carbs,
            "estimated_daily_fat_g": estimated_fat,
            "caloric_surplus": estimated_calories - base_calories,
            "nutrition_readiness": round(min(1.0, avg_weekly_sets / 100), 3),
        }

    def _simulate_decision(self, plan_data: dict[str, Any]) -> dict[str, Any]:
        """Simulate the Decision Engine output.

        Aggregates all simulation outputs into a go/no-go recommendation.
        """
        prediction = plan_data.get("prediction", {})
        recovery = plan_data.get("recovery", {})
        nutrition = plan_data.get("nutrition", {})

        vol_score = prediction.get("volume_response_score", 0.5)
        rec_score = recovery.get("fatigue_score", 0.5)
        nut_score = nutrition.get("nutrition_readiness", 0.5)

        composite = vol_score * 0.4 + rec_score * 0.35 + nut_score * 0.25

        return {
            "composite_readiness": round(composite, 3),
            "is_recommended": composite >= 0.5,
            "vol_verdict": "sufficient" if vol_score >= 0.5 else "insufficient",
            "rec_verdict": "sustainable" if rec_score >= 0.5 else "overreaching",
            "nut_verdict": "adequate" if nut_score >= 0.5 else "inadequate",
            "risk_assessment": "low" if composite >= 0.7 else "moderate" if composite >= 0.4 else "high",
        }

    def _compute_scores(
        self,
        plan_data: dict[str, Any],
        objectives: list[OptimizationObjective],
        constraints: list[OptimizationConstraint],
    ) -> OptimizationScore:
        return CompositeScorer.score(plan_data, objectives, constraints)

    def compute_result(
        self,
        request_id: str,
        all_candidates: list[OptimizationCandidate],
        total_generations: int,
        duration_seconds: float = 0.0,
        completed_at: str = "",
    ) -> OptimizationResult:
        feasible = [c for c in all_candidates if c.is_feasible]
        best = max(feasible, key=lambda c: c.scores.overall) if feasible else None

        return OptimizationResult(
            result_id=_generate_id("result"),
            request_id=request_id,
            best_candidate=best,
            all_candidates=all_candidates,
            final_score=best.scores.overall if best else 0.0,
            total_generations=total_generations,
            total_evaluated=len(all_candidates),
            feasible_count=len(feasible),
            status=OptimizerStatus.COMPLETED,
            duration_seconds=duration_seconds,
            completed_at=completed_at,
        )
