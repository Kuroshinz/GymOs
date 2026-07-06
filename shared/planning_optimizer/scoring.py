"""Planning Optimizer Scoring — Composite scoring engine combining objectives and constraints into a single quality score."""

from __future__ import annotations

from typing import Any

from shared.planning_optimizer.constraints import ConstraintChecker
from shared.planning_optimizer.domain import (
    OptimizationConstraint,
    OptimizationObjective,
    OptimizationScore,
)
from shared.planning_optimizer.objectives import ObjectiveScorer


class CompositeScorer:
    """Computes the six-component composite score for a candidate plan.

    Always deterministic — pure function of plan data + objectives + constraints.
    """

    SCIENTIFIC_OBJECTIVES = frozenset({
        "maximize_hypertrophy", "balance_volume", "maximize_progression",
        "maximize_strength", "maximize_endurance",
    })
    RECOVERY_OBJECTIVES = frozenset({
        "minimize_fatigue", "maximize_recovery",
    })
    HYPERTROPHY_TARGETS = frozenset({
        "maximize_hypertrophy",
    })

    @staticmethod
    def score(
        plan_data: dict[str, Any],
        objectives: list[OptimizationObjective],
        constraints: list[OptimizationConstraint],
        constraint_penalty_factor: float = 0.3,
    ) -> OptimizationScore:
        """Compute the full composite score for a plan candidate."""
        scientific_score = CompositeScorer._compute_scientific_score(plan_data, objectives)
        recovery_score = CompositeScorer._compute_recovery_score(plan_data, objectives)
        hypertrophy_score = CompositeScorer._compute_hypertrophy_score(plan_data, objectives)
        compliance_score = CompositeScorer._compute_compliance_score(plan_data, objectives)
        risk_score = CompositeScorer._compute_risk_score(plan_data, objectives)

        constraint_penalty = ConstraintChecker.compute_penalty(
            plan_data, constraints, constraint_penalty_factor
        )

        raw_overall = (
            scientific_score * 0.25 +
            recovery_score * 0.15 +
            hypertrophy_score * 0.25 +
            compliance_score * 0.20 +
            risk_score * 0.15
        )

        overall = raw_overall * (1.0 - constraint_penalty)

        return OptimizationScore(
            scientific_score=scientific_score,
            recovery_score=recovery_score,
            hypertrophy_score=hypertrophy_score,
            compliance_score=compliance_score,
            risk_score=risk_score,
            overall=max(0.0, min(1.0, overall)),
        )

    @staticmethod
    def _compute_scientific_score(
        plan_data: dict[str, Any],
        objectives: list[OptimizationObjective],
    ) -> float:
        scientific_objs = [
            o for o in objectives
            if o.objective_type.value in CompositeScorer.SCIENTIFIC_OBJECTIVES
        ]
        if scientific_objs:
            return ObjectiveScorer.compute_weighted_score(scientific_objs, plan_data)
        return ObjectiveScorer.score_progression_quality(plan_data) * 0.5 + 0.25

    @staticmethod
    def _compute_recovery_score(
        plan_data: dict[str, Any],
        objectives: list[OptimizationObjective],
    ) -> float:
        recovery_objs = [
            o for o in objectives
            if o.objective_type.value in CompositeScorer.RECOVERY_OBJECTIVES
        ]
        if recovery_objs:
            return ObjectiveScorer.compute_weighted_score(recovery_objs, plan_data)
        return ObjectiveScorer.score_recovery(plan_data) * 0.5 + 0.25

    @staticmethod
    def _compute_hypertrophy_score(
        plan_data: dict[str, Any],
        objectives: list[OptimizationObjective],
    ) -> float:
        hypertrophy_objs = [
            o for o in objectives
            if o.objective_type.value in CompositeScorer.HYPERTROPHY_TARGETS
        ]
        if hypertrophy_objs:
            return ObjectiveScorer.compute_weighted_score(hypertrophy_objs, plan_data)
        return ObjectiveScorer.score_hypertrophy(plan_data) * 0.5 + 0.25

    @staticmethod
    def _compute_compliance_score(
        plan_data: dict[str, Any],
        objectives: list[OptimizationObjective],
    ) -> float:
        adherence_obj = next(
            (o for o in objectives if o.objective_type.value == "maximize_adherence"),
            None,
        )
        if adherence_obj:
            return ObjectiveScorer.compute_objective_score(adherence_obj, plan_data)
        return ObjectiveScorer.score_adherence(plan_data) * 0.5 + 0.25

    @staticmethod
    def _compute_risk_score(
        plan_data: dict[str, Any],
        objectives: list[OptimizationObjective],
    ) -> float:
        plateau_obj = next(
            (o for o in objectives if o.objective_type.value == "minimize_plateau_risk"),
            None,
        )
        injury_obj = next(
            (o for o in objectives if o.objective_type.value == "minimize_injury_risk"),
            None,
        )
        if plateau_obj and injury_obj:
            return (
                ObjectiveScorer.compute_objective_score(plateau_obj, plan_data) * 0.5 +
                ObjectiveScorer.compute_objective_score(injury_obj, plan_data) * 0.5
            )
        if plateau_obj:
            return ObjectiveScorer.compute_objective_score(plateau_obj, plan_data)
        if injury_obj:
            return ObjectiveScorer.compute_objective_score(injury_obj, plan_data)
        return (
            ObjectiveScorer.score_plateau_risk(plan_data) * 0.5 +
            ObjectiveScorer.score_injury_risk(plan_data) * 0.5
        ) * 0.5 + 0.25
