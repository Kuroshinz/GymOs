"""Planning Serializer — converts planning domain models to/from dictionaries and JSON."""

from __future__ import annotations

import json
from typing import Any

from shared.planning.domain import (
    CyclePhase,
    DayType,
    ExerciseAllocation,
    FatigueBudget,
    IntensityDomain,
    Macrocycle,
    Mesocycle,
    MesocycleGoal,
    Microcycle,
    NutritionBudget,
    PlanningState,
    PlanProgress,
    ProgressionModel,
    RecoveryBudget,
    SessionPlan,
    TrainingFocus,
    VolumeAllocation,
    WeekPlan,
)
from shared.planning.metrics import (
    PlanningMetrics,
    PlanQuality,
)
from shared.planning.validator import ValidationResult


class PlanningSerializer:
    """Serializes planning models to/from dict and JSON."""

    @staticmethod
    def macrocycle_to_dict(macrocycle: Macrocycle) -> dict[str, Any]:
        return {
            "macrocycle_id": macrocycle.macrocycle_id,
            "name": macrocycle.name,
            "duration_weeks": macrocycle.duration_weeks,
            "start_date": macrocycle.start_date,
            "end_date": macrocycle.end_date,
            "overall_goal": macrocycle.overall_goal,
            "user_intent_id": macrocycle.user_intent_id,
            "version": macrocycle.version,
            "mesocycles": [
                PlanningSerializer.mesocycle_to_dict(m)
                for m in macrocycle.mesocycles
            ],
        }

    @staticmethod
    def macrocycle_from_dict(data: dict[str, Any]) -> Macrocycle:
        return Macrocycle(
            macrocycle_id=data.get("macrocycle_id", ""),
            name=data.get("name", ""),
            duration_weeks=data.get("duration_weeks", 24),
            start_date=data.get("start_date", ""),
            end_date=data.get("end_date", ""),
            mesocycles=[
                PlanningSerializer.mesocycle_from_dict(m)
                for m in data.get("mesocycles", [])
            ],
            overall_goal=data.get("overall_goal", ""),
            user_intent_id=data.get("user_intent_id", ""),
            version=data.get("version", "1.0"),
        )

    @staticmethod
    def mesocycle_to_dict(mesocycle: Mesocycle) -> dict[str, Any]:
        return {
            "mesocycle_id": mesocycle.mesocycle_id,
            "name": mesocycle.name,
            "goal": mesocycle.goal.value,
            "focus": mesocycle.focus.value,
            "phase": mesocycle.phase.value,
            "week_count": mesocycle.week_count,
            "start_week": mesocycle.start_week,
            "target_rir": mesocycle.target_rir,
            "target_rpe": mesocycle.target_rpe,
            "min_volume_per_muscle": mesocycle.min_volume_per_muscle,
            "max_volume_per_muscle": mesocycle.max_volume_per_muscle,
            "intensity_zone": mesocycle.intensity_zone.value,
            "deload_after": mesocycle.deload_after,
            "microcycles": [
                PlanningSerializer.microcycle_to_dict(m)
                for m in mesocycle.microcycles
            ],
        }

    @staticmethod
    def mesocycle_from_dict(data: dict[str, Any]) -> Mesocycle:
        return Mesocycle(
            mesocycle_id=data.get("mesocycle_id", ""),
            name=data.get("name", ""),
            goal=MesocycleGoal(data.get("goal", "hypertrophy")),
            focus=TrainingFocus(data.get("focus", "hypertrophy")),
            phase=CyclePhase(data.get("phase", "hypertrophy_i")),
            microcycles=[
                PlanningSerializer.microcycle_from_dict(m)
                for m in data.get("microcycles", [])
            ],
            week_count=data.get("week_count", 5),
            start_week=data.get("start_week", 0),
            target_rir=data.get("target_rir", 1.0),
            target_rpe=data.get("target_rpe", 8.0),
            min_volume_per_muscle=data.get("min_volume_per_muscle", 8),
            max_volume_per_muscle=data.get("max_volume_per_muscle", 22),
            intensity_zone=IntensityDomain(data.get("intensity_zone", "hypertrophy")),
            deload_after=data.get("deload_after", True),
        )

    @staticmethod
    def microcycle_to_dict(microcycle: Microcycle) -> dict[str, Any]:
        return {
            "microcycle_id": microcycle.microcycle_id,
            "phase": microcycle.phase.value,
            "focus": microcycle.focus.value,
            "progression_model": microcycle.progression_model.value,
            "week_count": microcycle.week_count,
            "start_week": microcycle.start_week,
            "weeks": [PlanningSerializer.week_to_dict(w) for w in microcycle.weeks],
        }

    @staticmethod
    def microcycle_from_dict(data: dict[str, Any]) -> Microcycle:
        return Microcycle(
            microcycle_id=data.get("microcycle_id", ""),
            phase=CyclePhase(data.get("phase", "hypertrophy_i")),
            weeks=[PlanningSerializer.week_from_dict(w) for w in data.get("weeks", [])],
            focus=TrainingFocus(data.get("focus", "hypertrophy")),
            progression_model=ProgressionModel(data.get("progression_model", "double_progression")),
            week_count=data.get("week_count", 4),
            start_week=data.get("start_week", 0),
        )

    @staticmethod
    def week_to_dict(week: WeekPlan) -> dict[str, Any]:
        return {
            "week_number": week.week_number,
            "start_date": week.start_date,
            "end_date": week.end_date,
            "is_deload_week": week.is_deload_week,
            "is_transition_week": week.is_transition_week,
            "sessions": [PlanningSerializer.session_to_dict(s) for s in week.sessions],
            "recovery_budget": PlanningSerializer.recovery_budget_to_dict(week.recovery_budget),
            "nutrition_budget": PlanningSerializer.nutrition_budget_to_dict(week.nutrition_budget),
            "notes": week.notes,
        }

    @staticmethod
    def week_from_dict(data: dict[str, Any]) -> WeekPlan:
        return WeekPlan(
            week_number=data.get("week_number", 0),
            start_date=data.get("start_date", ""),
            end_date=data.get("end_date", ""),
            sessions=[PlanningSerializer.session_from_dict(s) for s in data.get("sessions", [])],
            is_deload_week=data.get("is_deload_week", False),
            is_transition_week=data.get("is_transition_week", False),
            recovery_budget=PlanningSerializer.recovery_budget_from_dict(
                data.get("recovery_budget", {})
            ),
            nutrition_budget=PlanningSerializer.nutrition_budget_from_dict(
                data.get("nutrition_budget", {})
            ),
            notes=data.get("notes", ""),
        )

    @staticmethod
    def session_to_dict(session: SessionPlan) -> dict[str, Any]:
        return {
            "session_id": session.session_id,
            "week": session.week,
            "day_of_week": session.day_of_week,
            "day_type": session.day_type.value,
            "training_focus": session.training_focus.value,
            "estimated_duration_minutes": session.estimated_duration_minutes,
            "is_deload": session.is_deload,
            "is_recovery": session.is_recovery,
            "notes": session.notes,
            "exercises": [
                PlanningSerializer.exercise_to_dict(e)
                for e in session.exercises
            ],
            "volume_allocation": PlanningSerializer.volume_allocation_to_dict(
                session.volume_allocation
            ),
        }

    @staticmethod
    def session_from_dict(data: dict[str, Any]) -> SessionPlan:
        return SessionPlan(
            session_id=data.get("session_id", ""),
            week=data.get("week", 0),
            day_of_week=data.get("day_of_week", 0),
            day_type=DayType(data.get("day_type", "rest")),
            training_focus=TrainingFocus(data.get("training_focus", "hypertrophy")),
            exercises=[
                PlanningSerializer.exercise_from_dict(e)
                for e in data.get("exercises", [])
            ],
            volume_allocation=PlanningSerializer.volume_allocation_from_dict(
                data.get("volume_allocation", {})
            ),
            estimated_duration_minutes=data.get("estimated_duration_minutes", 60),
            is_deload=data.get("is_deload", False),
            is_recovery=data.get("is_recovery", False),
            notes=data.get("notes", ""),
        )

    @staticmethod
    def exercise_to_dict(exercise: ExerciseAllocation) -> dict[str, Any]:
        return {
            "exercise_id": exercise.exercise_id,
            "exercise_name": exercise.exercise_name,
            "target_muscle_group": exercise.target_muscle_group,
            "sets": exercise.sets,
            "reps": exercise.reps,
            "rir": exercise.rir,
            "rpe": exercise.rpe,
            "load_percent": exercise.load_percent,
            "rest_seconds": exercise.rest_seconds,
            "is_warmup": exercise.is_warmup,
            "is_primary": exercise.is_primary,
            "order_in_session": exercise.order_in_session,
        }

    @staticmethod
    def exercise_from_dict(data: dict[str, Any]) -> ExerciseAllocation:
        return ExerciseAllocation(
            exercise_id=data.get("exercise_id", ""),
            exercise_name=data.get("exercise_name", ""),
            target_muscle_group=data.get("target_muscle_group", ""),
            sets=data.get("sets", 0),
            reps=data.get("reps", 0),
            rir=data.get("rir", 1.0),
            rpe=data.get("rpe"),
            load_percent=data.get("load_percent", 0.0),
            rest_seconds=data.get("rest_seconds", 90),
            is_warmup=data.get("is_warmup", False),
            is_primary=data.get("is_primary", False),
            order_in_session=data.get("order_in_session", 0),
        )

    @staticmethod
    def volume_allocation_to_dict(va: VolumeAllocation) -> dict[str, Any]:
        return {
            "sets_per_exercise": list(va.sets_per_exercise),
            "reps_per_set": list(va.reps_per_set),
            "total_sets_per_session": va.total_sets_per_session,
            "total_sets_per_muscle_group": va.total_sets_per_muscle_group,
            "rir_target": va.rir_target,
            "rpe_cap": va.rpe_cap,
            "intensity_percent": list(va.intensity_percent),
        }

    @staticmethod
    def volume_allocation_from_dict(data: dict[str, Any]) -> VolumeAllocation:
        spe = data.get("sets_per_exercise", [3, 5])
        rps = data.get("reps_per_set", [6, 12])
        ip = data.get("intensity_percent", [0.65, 0.80])
        return VolumeAllocation(
            sets_per_exercise=(spe[0], spe[1]) if len(spe) >= 2 else (3, 5),
            reps_per_set=(rps[0], rps[1]) if len(rps) >= 2 else (6, 12),
            total_sets_per_session=data.get("total_sets_per_session", 15),
            total_sets_per_muscle_group=data.get("total_sets_per_muscle_group", 12),
            rir_target=data.get("rir_target", 1.0),
            rpe_cap=data.get("rpe_cap", 9.0),
            intensity_percent=(ip[0], ip[1]) if len(ip) >= 2 else (0.65, 0.80),
        )

    @staticmethod
    def fatigue_budget_to_dict(fb: FatigueBudget) -> dict[str, Any]:
        return {
            "total_fatigue_units": fb.total_fatigue_units,
            "used_fatigue_units": fb.used_fatigue_units,
            "max_per_session": fb.max_per_session,
            "max_per_muscle_group": fb.max_per_muscle_group,
            "recovery_rate_per_day": fb.recovery_rate_per_day,
            "current_fatigue_level": fb.current_fatigue_level,
        }

    @staticmethod
    def recovery_budget_to_dict(rb: RecoveryBudget) -> dict[str, Any]:
        return {
            "available_hours_per_night": rb.available_hours_per_night,
            "target_hrv_score": rb.target_hrv_score,
            "current_hrv_score": rb.current_hrv_score,
            "sleep_quality_score": rb.sleep_quality_score,
            "nutrition_score": rb.nutrition_score,
            "stress_level": rb.stress_level,
            "readiness_score": rb.readiness_score,
            "active_recovery_minutes_per_week": rb.active_recovery_minutes_per_week,
            "rest_days_per_week": rb.rest_days_per_week,
        }

    @staticmethod
    def recovery_budget_from_dict(data: dict[str, Any]) -> RecoveryBudget:
        return RecoveryBudget(
            available_hours_per_night=data.get("available_hours_per_night", 8.0),
            target_hrv_score=data.get("target_hrv_score", 65.0),
            current_hrv_score=data.get("current_hrv_score", 60.0),
            sleep_quality_score=data.get("sleep_quality_score", 0.75),
            nutrition_score=data.get("nutrition_score", 0.70),
            stress_level=data.get("stress_level", 5.0),
            readiness_score=data.get("readiness_score", 0.75),
            active_recovery_minutes_per_week=data.get("active_recovery_minutes_per_week", 60),
            rest_days_per_week=data.get("rest_days_per_week", 2),
        )

    @staticmethod
    def nutrition_budget_to_dict(nb: NutritionBudget) -> dict[str, Any]:
        return {
            "target_calories": nb.target_calories,
            "protein_g": nb.protein_g,
            "carbs_g": nb.carbs_g,
            "fat_g": nb.fat_g,
            "fiber_g": nb.fiber_g,
            "hydration_ml": nb.hydration_ml,
            "pre_workout_carbs_g": nb.pre_workout_carbs_g,
            "post_workout_protein_g": nb.post_workout_protein_g,
            "meal_count": nb.meal_count,
        }

    @staticmethod
    def nutrition_budget_from_dict(data: dict[str, Any]) -> NutritionBudget:
        return NutritionBudget(
            target_calories=data.get("target_calories", 2500),
            protein_g=data.get("protein_g", 150),
            carbs_g=data.get("carbs_g", 300),
            fat_g=data.get("fat_g", 70),
            fiber_g=data.get("fiber_g", 30),
            hydration_ml=data.get("hydration_ml", 3000),
            pre_workout_carbs_g=data.get("pre_workout_carbs_g", 30),
            post_workout_protein_g=data.get("post_workout_protein_g", 40),
            meal_count=data.get("meal_count", 4),
        )

    # ── Serialization to/from JSON ─────────────────────────────────

    @staticmethod
    def macrocycle_to_json(macrocycle: Macrocycle, indent: int = 2) -> str:
        return json.dumps(
            PlanningSerializer.macrocycle_to_dict(macrocycle), indent=indent
        )

    @staticmethod
    def macrocycle_from_json(json_str: str) -> Macrocycle:
        return PlanningSerializer.macrocycle_from_dict(json.loads(json_str))

    @staticmethod
    def plan_quality_to_dict(pq: PlanQuality) -> dict[str, Any]:
        return {
            "overall": pq.overall,
            "scientific_score": pq.scientific_score,
            "recovery_balance": pq.recovery_balance,
            "fatigue_balance": pq.fatigue_balance,
            "specificity": pq.specificity,
            "adherence_prediction": pq.adherence_prediction,
            "volume_distribution": pq.volume_distribution,
            "progression_quality": pq.progression_quality,
            "grade": pq.grade,
        }

    @staticmethod
    def validation_to_dict(vr: ValidationResult) -> dict[str, Any]:
        return {
            "is_valid": vr.is_valid,
            "error_count": vr.error_count,
            "warning_count": vr.warning_count,
            "errors": [
                {"field": e.field, "message": e.message, "code": e.code}
                for e in vr.errors
            ],
            "warnings": [
                {"field": e.field, "message": e.message, "code": e.code}
                for e in vr.warnings
            ],
        }

    @staticmethod
    def metrics_to_dict(metrics: PlanningMetrics) -> dict[str, Any]:
        return {
            "total_plans": metrics.total_plans,
            "active_plans": metrics.active_plans,
            "completed_plans": metrics.completed_plans,
            "avg_plan_quality": metrics.avg_plan_quality,
            "avg_scientific_score": metrics.avg_scientific_score,
            "avg_recovery_balance": metrics.avg_recovery_balance,
            "avg_fatigue_balance": metrics.avg_fatigue_balance,
            "avg_specificity": metrics.avg_specificity,
            "avg_adherence_prediction": metrics.avg_adherence_prediction,
            "total_validation_errors": metrics.total_validation_errors,
            "total_validation_warnings": metrics.total_validation_warnings,
            "total_mesocycles": metrics.total_mesocycles,
            "total_sessions": metrics.total_sessions,
            "total_sets": metrics.total_sets,
        }

    @staticmethod
    def state_to_dict(state: PlanningState) -> dict[str, Any]:
        return {
            "has_active_plan": state.has_active_plan,
            "active_macrocycle_id": state.active_macrocycle_id,
            "plan_count": state.plan_count,
            "last_updated": state.last_updated,
            "current_phase": state.current_phase.value if state.current_phase else None,
        }

    @staticmethod
    def progress_to_dict(progress: PlanProgress) -> dict[str, Any]:
        return {
            "weeks_completed": progress.weeks_completed,
            "sessions_completed": progress.sessions_completed,
            "total_weeks": progress.total_weeks,
            "total_sessions": progress.total_sessions,
            "adherence_rate": progress.adherence_rate,
            "completion_percent": progress.completion_percent,
            "is_complete": progress.is_complete,
        }
