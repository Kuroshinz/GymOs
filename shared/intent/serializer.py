from __future__ import annotations

import json
from typing import Any

from shared.intent.builder import IntentBuilder
from shared.intent.domain import (
    IntentSnapshot,
    UserIntent,
)


class IntentSerializer:
    @staticmethod
    def to_dict(intent: UserIntent) -> dict[str, Any]:
        return {
            "intent_id": intent.intent_id,
            "version": intent.version,
            "status": intent.status.value,
            "created_at": intent.created_at,
            "updated_at": intent.updated_at,
            "goals": [
                {
                    "goal_type": g.goal_type.value,
                    "target_value": g.target_value,
                    "current_value": g.current_value,
                    "unit": g.unit,
                    "target_date": g.target_date,
                    "priority": g.priority,
                    "description": g.description,
                }
                for g in intent.goals
            ],
            "constraints": [
                {
                    "constraint_type": c.constraint_type.value,
                    "name": c.name,
                    "description": c.description,
                    "severity": c.severity,
                    "value": c.value,
                    "is_active": c.is_active,
                }
                for c in intent.constraints
            ],
            "timeline": {
                "sessions_per_week": intent.timeline.sessions_per_week,
                "session_duration_minutes": intent.timeline.session_duration_minutes,
                "preferred_days": [d.value for d in intent.timeline.preferred_days],
                "preferred_time": intent.timeline.preferred_time.value,
                "available_start_hour": intent.timeline.available_start_hour,
                "available_end_hour": intent.timeline.available_end_hour,
            },
            "equipment": {
                "level": intent.equipment.level.value,
                "available_items": list(intent.equipment.available_items),
                "missing_items": list(intent.equipment.missing_items),
                "home_items": list(intent.equipment.home_items),
            },
            "lifestyle": {
                "occupation": intent.lifestyle.occupation,
                "occupation_hours_per_week": intent.lifestyle.occupation_hours_per_week,
                "commute_minutes_per_day": intent.lifestyle.commute_minutes_per_day,
                "sleep_target_hours": intent.lifestyle.sleep_target_hours,
                "sleep_avg_hours": intent.lifestyle.sleep_avg_hours,
                "stress_level": intent.lifestyle.stress_level,
                "has_children": intent.lifestyle.has_children,
                "social_commitments_per_week": intent.lifestyle.social_commitments_per_week,
            },
            "compliance": {
                "training_compliance_rate": intent.compliance.training_compliance_rate,
                "nutrition_compliance_rate": intent.compliance.nutrition_compliance_rate,
                "recovery_compliance_rate": intent.compliance.recovery_compliance_rate,
                "streak_days": intent.compliance.streak_days,
                "avg_missed_per_month": intent.compliance.avg_missed_per_month,
                "common_skip_reasons": list(intent.compliance.common_skip_reasons),
            },
            "risk_tolerance": {
                "training_risk": intent.risk_tolerance.training_risk.value,
                "nutrition_risk": intent.risk_tolerance.nutrition_risk.value,
                "recovery_risk": intent.risk_tolerance.recovery_risk.value,
            },
            "training": {
                "style": intent.training.style.value,
                "focus_muscles": list(intent.training.focus_muscles),
                "priority_muscle_groups": list(intent.training.priority_muscle_groups),
                "min_volume_per_muscle": intent.training.min_volume_per_muscle,
                "max_volume_per_muscle": intent.training.max_volume_per_muscle,
                "prefer_compound_first": intent.training.prefer_compound_first,
                "warmup_minutes": intent.training.warmup_minutes,
                "cardio_minutes_per_week": intent.training.cardio_minutes_per_week,
                "progression_style": intent.training.progression_style,
                "deload_frequency_weeks": intent.training.deload_frequency_weeks,
                "rpe_target_max": intent.training.rpe_target_max,
                "rir_target_min": intent.training.rir_target_min,
                "rest_minutes_between_sets": intent.training.rest_minutes_between_sets,
            },
            "nutrition": {
                "approach": intent.nutrition.approach.value,
                "protein_g_per_kg": intent.nutrition.protein_g_per_kg,
                "fat_min_g": intent.nutrition.fat_min_g,
                "fiber_g": intent.nutrition.fiber_g,
                "meal_count_per_day": intent.nutrition.meal_count_per_day,
                "prefer_whole_foods": intent.nutrition.prefer_whole_foods,
                "allow_supplements": intent.nutrition.allow_supplements,
                "hydration_ml_per_day": intent.nutrition.hydration_ml_per_day,
                "caffeine_mg_per_day": intent.nutrition.caffeine_mg_per_day,
                "meal_prep_sunday": intent.nutrition.meal_prep_sunday,
            },
            "recovery": {
                "priority": intent.recovery.priority.value,
                "sleep_target": intent.recovery.sleep_target,
                "sleep_minimum": intent.recovery.sleep_minimum,
                "track_hrv": intent.recovery.track_hrv,
                "track_soreness": intent.recovery.track_soreness,
                "auto_deload": intent.recovery.auto_deload,
                "deload_trigger_fatigue": intent.recovery.deload_trigger_fatigue,
                "recovery_checkin_weekly": intent.recovery.recovery_checkin_weekly,
                "stress_management": intent.recovery.stress_management,
            },
            "adaptive": {
                "enabled_scopes": [s.value for s in intent.adaptive.enabled_scopes],
                "require_approval": intent.adaptive.require_approval,
                "max_change_percent": intent.adaptive.max_change_percent,
                "adaptation_speed": intent.adaptive.adaptation_speed,
                "learning_period_days": intent.adaptive.learning_period_days,
                "min_data_points": intent.adaptive.min_data_points,
            },
            "priorities": {
                "training_priority": intent.priorities.training_priority,
                "nutrition_priority": intent.priorities.nutrition_priority,
                "recovery_priority": intent.priorities.recovery_priority,
                "consistency_priority": intent.priorities.consistency_priority,
                "lifestyle_priority": intent.priorities.lifestyle_priority,
            },
            "conflicts": [
                {
                    "dimension_a": c.dimension_a,
                    "dimension_b": c.dimension_b,
                    "description": c.description,
                    "severity": c.severity.value,
                    "resolution": c.resolution,
                    "is_resolved": c.is_resolved,
                }
                for c in intent.conflicts
            ],
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> UserIntent:
        return IntentBuilder.build(data)

    @staticmethod
    def to_json(intent: UserIntent, indent: int = 2) -> str:
        return json.dumps(IntentSerializer.to_dict(intent), indent=indent)

    @staticmethod
    def from_json(json_str: str) -> UserIntent:
        data = json.loads(json_str)
        return IntentSerializer.from_dict(data)

    @staticmethod
    def snapshot_to_dict(snapshot: IntentSnapshot) -> dict[str, Any]:
        return {
            "intent": IntentSerializer.to_dict(snapshot.intent),
            "timestamp": snapshot.timestamp,
            "snapshot_version": snapshot.snapshot_version,
            "score": snapshot.score,
            "change_description": snapshot.change_description,
        }
