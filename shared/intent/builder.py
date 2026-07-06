from __future__ import annotations

from datetime import datetime
from typing import Any

from shared.intent.domain import (
    AdaptivePreference,
    AdaptiveScope,
    ComplianceProfile,
    Constraint,
    ConstraintType,
    DayPreference,
    EquipmentLevel,
    EquipmentProfile,
    GoalIntent,
    GoalType,
    IntentStatus,
    LifestyleProfile,
    NutritionApproach,
    NutritionPreference,
    Priority,
    RecoveryPreference,
    RecoveryPriority,
    RiskLevel,
    RiskTolerance,
    Timeline,
    TimeOfDay,
    TrainingPreference,
    TrainingStyle,
    UserIntent,
)


class IntentBuilder:
    """Builds a UserIntent from raw configuration dictionaries.

    Deterministic — same inputs always produce the same intent.
    """

    @staticmethod
    def build(config: dict[str, Any]) -> UserIntent:
        now = datetime.now().isoformat()
        return UserIntent(
            intent_id=config.get("intent_id", ""),
            version=config.get("version", "1.0"),
            status=IntentStatus.ACTIVE,
            created_at=config.get("created_at", now),
            updated_at=config.get("updated_at", now),
            goals=IntentBuilder._build_goals(config.get("goals", [])),
            constraints=IntentBuilder._build_constraints(config.get("constraints", [])),
            timeline=IntentBuilder._build_timeline(config.get("timeline", {})),
            equipment=IntentBuilder._build_equipment(config.get("equipment", {})),
            lifestyle=IntentBuilder._build_lifestyle(config.get("lifestyle", {})),
            compliance=IntentBuilder._build_compliance(config.get("compliance", {})),
            risk_tolerance=IntentBuilder._build_risk_tolerance(config.get("risk_tolerance", {})),
            training=IntentBuilder._build_training(config.get("training", {})),
            nutrition=IntentBuilder._build_nutrition(config.get("nutrition", {})),
            recovery=IntentBuilder._build_recovery(config.get("recovery", {})),
            adaptive=IntentBuilder._build_adaptive(config.get("adaptive", {})),
            priorities=IntentBuilder._build_priorities(config.get("priorities", {})),
        )

    @staticmethod
    def _build_goals(data: list[dict[str, Any]]) -> list[GoalIntent]:
        return [GoalIntent(
            goal_type=GoalType(g.get("goal_type", "hypertrophy")),
            target_value=g.get("target_value", 0.0),
            current_value=g.get("current_value", 0.0),
            unit=g.get("unit", ""),
            target_date=g.get("target_date", ""),
            priority=g.get("priority", 5),
            description=g.get("description", ""),
        ) for g in data]

    @staticmethod
    def _build_constraints(data: list[dict[str, Any]]) -> list[Constraint]:
        return [Constraint(
            constraint_type=ConstraintType(c.get("constraint_type", "time")),
            name=c.get("name", ""),
            description=c.get("description", ""),
            severity=c.get("severity", "medium"),
            value=c.get("value", ""),
            is_active=c.get("is_active", True),
        ) for c in data]

    @staticmethod
    def _build_timeline(data: dict[str, Any]) -> Timeline:
        raw_days = data.get("preferred_days", ["everyday"])
        preferred_days = [DayPreference(d) if isinstance(d, str) else d for d in raw_days]
        raw_time = data.get("preferred_time", "flexible")
        preferred_time = TimeOfDay(raw_time) if isinstance(raw_time, str) else raw_time
        return Timeline(
            sessions_per_week=data.get("sessions_per_week", 5),
            session_duration_minutes=data.get("session_duration_minutes", 60),
            preferred_days=preferred_days,
            preferred_time=preferred_time,
            available_start_hour=data.get("available_start_hour", 6),
            available_end_hour=data.get("available_end_hour", 22),
        )

    @staticmethod
    def _build_equipment(data: dict[str, Any]) -> EquipmentProfile:
        return EquipmentProfile(
            level=EquipmentLevel(data.get("level", "commercial")),
            available_items=data.get("available_items", []),
            missing_items=data.get("missing_items", []),
            home_items=data.get("home_items", []),
        )

    @staticmethod
    def _build_lifestyle(data: dict[str, Any]) -> LifestyleProfile:
        return LifestyleProfile(
            occupation=data.get("occupation", ""),
            occupation_hours_per_week=data.get("occupation_hours_per_week", 40),
            commute_minutes_per_day=data.get("commute_minutes_per_day", 30),
            sleep_target_hours=data.get("sleep_target_hours", 8.0),
            sleep_avg_hours=data.get("sleep_avg_hours", 7.0),
            stress_level=data.get("stress_level", "moderate"),
            has_children=data.get("has_children", False),
            social_commitments_per_week=data.get("social_commitments_per_week", 2),
        )

    @staticmethod
    def _build_compliance(data: dict[str, Any]) -> ComplianceProfile:
        return ComplianceProfile(
            training_compliance_rate=data.get("training_compliance_rate", 0.85),
            nutrition_compliance_rate=data.get("nutrition_compliance_rate", 0.80),
            recovery_compliance_rate=data.get("recovery_compliance_rate", 0.70),
            streak_days=data.get("streak_days", 0),
            avg_missed_per_month=data.get("avg_missed_per_month", 2.0),
            common_skip_reasons=data.get("common_skip_reasons", []),
        )

    @staticmethod
    def _build_risk_tolerance(data: dict[str, Any]) -> RiskTolerance:
        return RiskTolerance(
            training_risk=RiskLevel(data.get("training_risk", "moderate")),
            nutrition_risk=RiskLevel(data.get("nutrition_risk", "conservative")),
            recovery_risk=RiskLevel(data.get("recovery_risk", "conservative")),
        )

    @staticmethod
    def _build_training(data: dict[str, Any]) -> TrainingPreference:
        return TrainingPreference(
            style=TrainingStyle(data.get("style", "ppl_ul")),
            focus_muscles=data.get("focus_muscles", []),
            priority_muscle_groups=data.get("priority_muscle_groups", []),
            min_volume_per_muscle=data.get("min_volume_per_muscle", 8),
            max_volume_per_muscle=data.get("max_volume_per_muscle", 22),
            prefer_compound_first=data.get("prefer_compound_first", True),
            warmup_minutes=data.get("warmup_minutes", 10),
            cardio_minutes_per_week=data.get("cardio_minutes_per_week", 60),
            progression_style=data.get("progression_style", "double_progression"),
            deload_frequency_weeks=data.get("deload_frequency_weeks", 6),
            rpe_target_max=data.get("rpe_target_max", 9.0),
            rir_target_min=data.get("rir_target_min", 0),
            rest_minutes_between_sets=data.get("rest_minutes_between_sets", 2),
        )

    @staticmethod
    def _build_nutrition(data: dict[str, Any]) -> NutritionPreference:
        return NutritionPreference(
            approach=NutritionApproach(data.get("approach", "lean_bulk")),
            protein_g_per_kg=data.get("protein_g_per_kg", 2.0),
            fat_min_g=data.get("fat_min_g", 60.0),
            fiber_g=data.get("fiber_g", 30.0),
            meal_count_per_day=data.get("meal_count_per_day", 4),
            prefer_whole_foods=data.get("prefer_whole_foods", True),
            allow_supplements=data.get("allow_supplements", True),
            hydration_ml_per_day=data.get("hydration_ml_per_day", 3000),
            caffeine_mg_per_day=data.get("caffeine_mg_per_day", 200),
            meal_prep_sunday=data.get("meal_prep_sunday", True),
        )

    @staticmethod
    def _build_recovery(data: dict[str, Any]) -> RecoveryPreference:
        return RecoveryPreference(
            priority=RecoveryPriority(data.get("priority", "balance_lifestyle")),
            sleep_target=data.get("sleep_target", 8.0),
            sleep_minimum=data.get("sleep_minimum", 6.0),
            track_hrv=data.get("track_hrv", False),
            track_soreness=data.get("track_soreness", True),
            auto_deload=data.get("auto_deload", True),
            deload_trigger_fatigue=data.get("deload_trigger_fatigue", 80.0),
            recovery_checkin_weekly=data.get("recovery_checkin_weekly", True),
            stress_management=data.get("stress_management", True),
        )

    @staticmethod
    def _build_adaptive(data: dict[str, Any]) -> AdaptivePreference:
        raw_scopes = data.get("enabled_scopes", ["volume", "deload_timing"])
        enabled_scopes = [AdaptiveScope(s) if isinstance(s, str) else s for s in raw_scopes]
        return AdaptivePreference(
            enabled_scopes=enabled_scopes,
            require_approval=data.get("require_approval", True),
            max_change_percent=data.get("max_change_percent", 20.0),
            adaptation_speed=data.get("adaptation_speed", "moderate"),
            learning_period_days=data.get("learning_period_days", 14),
            min_data_points=data.get("min_data_points", 10),
        )

    @staticmethod
    def _build_priorities(data: dict[str, Any]) -> Priority:
        return Priority(
            training_priority=data.get("training_priority", 5),
            nutrition_priority=data.get("nutrition_priority", 4),
            recovery_priority=data.get("recovery_priority", 3),
            consistency_priority=data.get("consistency_priority", 5),
            lifestyle_priority=data.get("lifestyle_priority", 3),
        )
