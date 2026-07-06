from __future__ import annotations

from dataclasses import dataclass, field

from shared.intent.domain import UserIntent


@dataclass
class ValidationError:
    field: str = ""
    message: str = ""
    code: str = ""


@dataclass
class ValidationResult:
    is_valid: bool = True
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)

    def add_error(self, field: str, message: str, code: str = "E000") -> None:
        self.errors.append(ValidationError(field=field, message=message, code=code))
        self.is_valid = False

    def add_warning(self, field: str, message: str, code: str = "W000") -> None:
        self.warnings.append(ValidationError(field=field, message=message, code=code))

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)


class IntentValidator:
    @staticmethod
    def validate(intent: UserIntent) -> ValidationResult:
        result = ValidationResult()
        IntentValidator._validate_goals(intent, result)
        IntentValidator._validate_timeline(intent, result)
        IntentValidator._validate_training(intent, result)
        IntentValidator._validate_nutrition(intent, result)
        IntentValidator._validate_recovery(intent, result)
        IntentValidator._validate_lifestyle(intent, result)
        IntentValidator._validate_adaptive(intent, result)
        return result

    @staticmethod
    def _validate_goals(intent: UserIntent, result: ValidationResult) -> None:
        if not intent.goals:
            result.add_error("goals", "At least one goal is required", "G001")
            return
        for g in intent.goals:
            if g.target_value <= 0:
                result.add_warning("goals.target_value", f"Goal '{g.description}' has zero target", "G002")
            if g.priority < 1 or g.priority > 10:
                result.add_error("goals.priority", f"Priority must be 1-10, got {g.priority}", "G003")

    @staticmethod
    def _validate_timeline(intent: UserIntent, result: ValidationResult) -> None:
        if intent.timeline.sessions_per_week < 1:
            result.add_error("timeline.sessions_per_week", "Must have at least 1 session per week", "T001")
        if intent.timeline.sessions_per_week > 14:
            result.add_warning("timeline.sessions_per_week", f"{intent.timeline.sessions_per_week} sessions/week is extremely high", "T002")
        if intent.timeline.session_duration_minutes < 20:
            result.add_error("timeline.session_duration_minutes", "Session duration too short", "T003")
        if intent.timeline.session_duration_minutes > 180:
            result.add_warning("timeline.session_duration_minutes", "Session duration >3h may cause burnout", "T004")
        if intent.timeline.available_start_hour >= intent.timeline.available_end_hour:
            result.add_error("timeline.available_hours", "Start hour must be before end hour", "T005")

    @staticmethod
    def _validate_training(intent: UserIntent, result: ValidationResult) -> None:
        if intent.training.min_volume_per_muscle < 4:
            result.add_warning("training.min_volume", "Minimum volume <4 sets may be insufficient", "TR001")
        if intent.training.max_volume_per_muscle > 30:
            result.add_warning("training.max_volume", "Maximum volume >30 sets exceeds typical MRV", "TR002")
        if intent.training.min_volume_per_muscle > intent.training.max_volume_per_muscle:
            result.add_error("training.volume_range", "Min volume exceeds max volume", "TR003")
        if intent.training.rpe_target_max > 10:
            result.add_error("training.rpe", "RPE cannot exceed 10", "TR004")
        if intent.training.deload_frequency_weeks < 3:
            result.add_warning("training.deload_frequency", "Deloading every <3 weeks may limit progress", "TR005")

    @staticmethod
    def _validate_nutrition(intent: UserIntent, result: ValidationResult) -> None:
        if intent.nutrition.protein_g_per_kg < 1.0:
            result.add_warning("nutrition.protein", "Protein <1g/kg is below minimum recommendations", "N001")
        if intent.nutrition.protein_g_per_kg > 3.5:
            result.add_warning("nutrition.protein", "Protein >3.5g/kg exceeds practical limits", "N002")
        if intent.nutrition.fat_min_g < 40:
            result.add_warning("nutrition.fat", "Fat <40g may impact hormone function", "N003")
        if intent.nutrition.hydration_ml_per_day < 1500:
            result.add_warning("nutrition.hydration", "Hydration <1500ml/day is insufficient", "N004")

    @staticmethod
    def _validate_recovery(intent: UserIntent, result: ValidationResult) -> None:
        if intent.recovery.sleep_target < 5:
            result.add_error("recovery.sleep_target", "Sleep target <5h is unsafe", "R001")
        if intent.recovery.sleep_target > 12:
            result.add_warning("recovery.sleep_target", "Sleep target >12h exceeds typical needs", "R002")
        if intent.recovery.sleep_minimum > intent.recovery.sleep_target:
            result.add_error("recovery.sleep_range", "Sleep minimum exceeds target", "R003")
        if intent.recovery.deload_trigger_fatigue < 50:
            result.add_warning("recovery.deload_trigger", "Very low deload trigger may cause unnecessary deloads", "R004")

    @staticmethod
    def _validate_lifestyle(intent: UserIntent, result: ValidationResult) -> None:
        if intent.lifestyle.occupation_hours_per_week > 80:
            result.add_warning("lifestyle.occupation_hours", "Extreme work hours may limit training capacity", "L001")
        weekly = (intent.timeline.sessions_per_week * intent.timeline.session_duration_minutes) / 60
        available = 168 - intent.lifestyle.occupation_hours_per_week - (intent.lifestyle.sleep_target_hours * 7)
        if weekly > available:
            result.add_warning("lifestyle.weekly_capacity", f"Training {weekly:.0f}h exceeds available {available:.0f}h", "L002")

    @staticmethod
    def _validate_adaptive(intent: UserIntent, result: ValidationResult) -> None:
        if intent.adaptive.max_change_percent <= 0:
            result.add_error("adaptive.max_change", "Max change percent must be positive", "A001")
        if intent.adaptive.max_change_percent > 50:
            result.add_warning("adaptive.max_change", "Changes >50% may be too aggressive", "A002")
        if intent.adaptive.learning_period_days < 7:
            result.add_warning("adaptive.learning_period", "Learning period <7 days may be insufficient", "A003")
        if intent.adaptive.min_data_points < 3:
            result.add_warning("adaptive.min_data_points", "Minimum 3 data points recommended for adaptation", "A004")
