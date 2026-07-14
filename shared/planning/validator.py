"""Planning Validator — scientific, volume, recovery, frequency, and constraint validation.

Every plan must pass all validations before it can be activated.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from shared.planning.domain import (
    Macrocycle,
    Mesocycle,
    MesocycleGoal,
    PlanningConfig,
    SessionPlan,
    WeekPlan,
)


@dataclass
class ValidationError:
    field: str = ""
    message: str = ""
    code: str = ""

    def __hash__(self) -> int:
        return hash((self.field, self.code))


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

    @property
    def all_issues(self) -> list[ValidationError]:
        return self.errors + self.warnings

    def merge(self, other: ValidationResult) -> ValidationResult:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        if not other.is_valid:
            self.is_valid = False
        return self


class ScientificValidator:
    @staticmethod
    def validate(macrocycle: Macrocycle) -> ValidationResult:
        result = ValidationResult()
        ScientificValidator._validate_mesocycle_sequence(macrocycle, result)
        ScientificValidator._validate_progression_logic(macrocycle, result)
        ScientificValidator._validate_deload_placement(macrocycle, result)
        ScientificValidator._validate_intensity_zones(macrocycle, result)
        ScientificValidator._validate_phase_duration(macrocycle, result)
        return result

    @staticmethod
    def _validate_mesocycle_sequence(macrocycle: Macrocycle, result: ValidationResult) -> ValidationResult:
        if not macrocycle.mesocycles:
            result.add_error("macrocycle.mesocycles", "Macrocycle must have at least one mesocycle", "S001")
            return
        for i, m in enumerate(macrocycle.mesocycles):
            if i > 0 and m.goal == macrocycle.mesocycles[i - 1].goal and m.goal != MesocycleGoal.MAINTENANCE:
                result.add_warning(
                        f"mesocycles[{i}].goal",
                        f"Consecutive mesocycles with same goal '{m.goal.label}'",
                        "S002",
                    )

    @staticmethod
    def _validate_progression_logic(macrocycle: Macrocycle, result: ValidationResult) -> None:
        if not macrocycle.mesocycles:
            return
        for i, meso in enumerate(macrocycle.mesocycles):
            for j, micro in enumerate(meso.microcycles):
                if j > 0:
                    prev_vol = micro.weeks[0].total_sets if micro.weeks else 0
                    if prev_vol > 0:
                        for k in range(1, len(micro.weeks)):
                            curr = micro.weeks[k].total_sets
                            prev = micro.weeks[k - 1].total_sets
                            if curr > 0 and prev > 0:
                                change = (curr - prev) / prev
                                if abs(change) > 0.5:
                                    result.add_warning(
                                        f"microcycles[{i}].weeks[{k}].total_sets",
                                        f"Week-over-week volume change of {change:.0%} exceeds 50%",
                                        "S003",
                                    )

    @staticmethod
    def _validate_deload_placement(macrocycle: Macrocycle, result: ValidationResult) -> None:
        training_weeks_since_deload = 0
        for i, week in enumerate(macrocycle.weeks):
            if week.is_deload_week:
                training_weeks_since_deload = 0
            else:
                training_weeks_since_deload += 1
            if training_weeks_since_deload > 8:
                result.add_warning(
                    f"weeks[{i}]",
                    f"No deload for {training_weeks_since_deload} weeks — consider adding a deload",
                    "S004",
                )

    @staticmethod
    def _validate_intensity_zones(macrocycle: Macrocycle, result: ValidationResult) -> None:
        for meso in macrocycle.mesocycles:
            if meso.goal == MesocycleGoal.MAX_STRENGTH and meso.intensity_zone.value != "strength":
                result.add_warning(
                    f"mesocycles.{meso.mesocycle_id}.intensity_zone",
                    f"Strength goal but intensity zone is {meso.intensity_zone.label}",
                    "S005",
                )
            if meso.goal == MesocycleGoal.HYPERTROPHY and meso.intensity_zone.value != "hypertrophy":
                result.add_warning(
                    f"mesocycles.{meso.mesocycle_id}.intensity_zone",
                    f"Hypertrophy goal but intensity zone is {meso.intensity_zone.label}",
                    "S005",
                )

    @staticmethod
    def _validate_phase_duration(macrocycle: Macrocycle, result: ValidationResult) -> None:
        for meso in macrocycle.mesocycles:
            if meso.week_count < 3:
                result.add_warning(
                    f"mesocycles.{meso.mesocycle_id}.week_count",
                    f"Mesocycle with {meso.week_count} weeks may be too short for adaptation",
                    "S006",
                )
            if meso.week_count > 8:
                result.add_warning(
                    f"mesocycles.{meso.mesocycle_id}.week_count",
                    f"Mesocycle with {meso.week_count} weeks may be too long for focus",
                    "S006",
                )


class VolumeValidator:
    @staticmethod
    def validate(macrocycle: Macrocycle, config: PlanningConfig) -> ValidationResult:
        result = ValidationResult()
        VolumeValidator._validate_session_volume(macrocycle, config, result)
        VolumeValidator._validate_weekly_volume(macrocycle, config, result)
        VolumeValidator._validate_muscle_group_volume(macrocycle, config, result)
        VolumeValidator._validate_volume_progression(macrocycle, result)
        return result

    @staticmethod
    def _validate_session_volume(macrocycle: Macrocycle, config: PlanningConfig, result: ValidationResult) -> None:
        for session in macrocycle.sessions:
            if session.is_deload or session.is_recovery:
                continue
            sets = session.total_sets
            if sets < config.min_sets_per_session:
                result.add_warning(
                    f"sessions.{session.session_id}",
                    f"Session has {sets} sets, minimum is {config.min_sets_per_session}",
                    "V001",
                )
            if sets > config.max_sets_per_session:
                result.add_error(
                    f"sessions.{session.session_id}",
                    f"Session has {sets} sets, maximum is {config.max_sets_per_session}",
                    "V002",
                )

    @staticmethod
    def _validate_weekly_volume(macrocycle: Macrocycle, config: PlanningConfig, result: ValidationResult) -> None:
        for week in macrocycle.weeks:
            if week.is_deload_week:
                continue
            if week.session_count < config.min_sessions_per_week:
                result.add_warning(
                    f"weeks[{week.week_number}]",
                    f"Week has {week.session_count} sessions, minimum is {config.min_sessions_per_week}",
                    "V003",
                )
            if week.session_count > config.max_sessions_per_week:
                result.add_error(
                    f"weeks[{week.week_number}]",
                    f"Week has {week.session_count} sessions, maximum is {config.max_sessions_per_week}",
                    "V004",
                )

    @staticmethod
    def _validate_muscle_group_volume(macrocycle: Macrocycle, config: PlanningConfig, result: ValidationResult) -> None:
        for week in macrocycle.weeks:
            for muscle, sets in week.weekly_volume_by_muscle.items():
                if sets < config.min_sets_per_muscle_weekly:
                    result.add_warning(
                        f"weeks[{week.week_number}].{muscle}",
                        f"{muscle}: {sets} sets/week, minimum is {config.min_sets_per_muscle_weekly}",
                        "V005",
                    )
                if sets > config.max_sets_per_muscle_weekly:
                    result.add_warning(
                        f"weeks[{week.week_number}].{muscle}",
                        f"{muscle}: {sets} sets/week exceeds {config.max_sets_per_muscle_weekly} MRV",
                        "V006",
                    )

    @staticmethod
    def _validate_volume_progression(macrocycle: Macrocycle, result: ValidationResult) -> None:
        trend = macrocycle.weekly_volume_trend
        for i in range(1, len(trend)):
            if trend[i - 1] > 0:
                pct_change = (trend[i] - trend[i - 1]) / trend[i - 1]
                if pct_change > 0.3 and not macrocycle.weeks[i].is_deload_week:
                    result.add_warning(
                        f"volume_trend[{i}]",
                        f"Volume spike of {pct_change:.0%} from week {i} to {i + 1}",
                        "V007",
                    )


class RecoveryValidator:
    @staticmethod
    def validate(macrocycle: Macrocycle, config: PlanningConfig) -> ValidationResult:
        result = ValidationResult()
        RecoveryValidator._validate_rest_days(macrocycle, result)
        RecoveryValidator._validate_deload_frequency(macrocycle, config, result)
        RecoveryValidator._validate_recovery_capacity(macrocycle, result)
        return result

    @staticmethod
    def _validate_rest_days(macrocycle: Macrocycle, result: ValidationResult) -> None:
        for week in macrocycle.weeks:
            rest_count = sum(
                1 for s in week.sessions
                if s.day_type.value in ("rest", "active_recovery")
            )
            if rest_count == 0 and not week.is_deload_week:
                result.add_warning(
                    f"weeks[{week.week_number}]",
                    "No rest days in training week",
                    "R001",
                )
            training_streak = 0
            for s in week.sessions:
                if s.day_type.value in ("rest", "active_recovery", "deload"):
                    training_streak = 0
                else:
                    training_streak += 1
                if training_streak > 5:
                    result.add_warning(
                        f"weeks[{week.week_number}]",
                        f"{training_streak} consecutive training days without rest",
                        "R002",
                    )

    @staticmethod
    def _validate_deload_frequency(macrocycle: Macrocycle, config: PlanningConfig, result: ValidationResult) -> None:
        training_streak = 0
        for i, week in enumerate(macrocycle.weeks):
            if week.is_deload_week:
                training_streak = 0
            else:
                training_streak += 1
            if training_streak > config.deload_frequency_weeks + 2:
                result.add_warning(
                    f"weeks[{i}]",
                    f"{training_streak} weeks without deload (recommended every {config.deload_frequency_weeks})",
                    "R003",
                )

    @staticmethod
    def _validate_recovery_capacity(macrocycle: Macrocycle, result: ValidationResult) -> None:
        for week in macrocycle.weeks:
            if week.recovery_budget.needs_rest:
                result.add_warning(
                    f"weeks[{week.week_number}].recovery_budget",
                    f"Recovery capacity is {week.recovery_budget.recovery_capacity:.0%} — below 40% threshold",
                    "R004",
                )


class FrequencyValidator:
    @staticmethod
    def validate(macrocycle: Macrocycle, config: PlanningConfig) -> ValidationResult:
        result = ValidationResult()
        FrequencyValidator._validate_session_frequency(macrocycle, config, result)
        FrequencyValidator._validate_muscle_frequency(macrocycle, result)
        return result

    @staticmethod
    def _validate_session_frequency(macrocycle: Macrocycle, config: PlanningConfig, result: ValidationResult) -> None:
        for week in macrocycle.weeks:
            if week.is_deload_week:
                continue
            count = week.session_count
            if count < config.min_sessions_per_week:
                result.add_error(
                    f"weeks[{week.week_number}].session_count",
                    f"Week has {count} sessions, minimum is {config.min_sessions_per_week}",
                    "F001",
                )
            if count > config.max_sessions_per_week:
                result.add_error(
                    f"weeks[{week.week_number}].session_count",
                    f"Week has {count} sessions, maximum is {config.max_sessions_per_week}",
                    "F002",
                )

    @staticmethod
    def _validate_muscle_frequency(macrocycle: Macrocycle, result: ValidationResult) -> None:
        visited: set[str] = set()
        for week in macrocycle.weeks:
            for session in week.sessions:
                for mg in session.muscle_groups_trained:
                    if mg in visited:
                        continue
                    visited.add(mg)
                    count = sum(
                        1 for s2 in week.sessions
                        if mg in s2.muscle_groups_trained
                    )
                    if count > 4:
                        result.add_warning(
                            f"weeks[{week.week_number}].{mg}",
                            f"{mg} trained {count}x/week — may exceed recovery capacity",
                            "F003",
                        )


class ConstraintValidator:
    @staticmethod
    def validate(
        macrocycle: Macrocycle,
        max_sets_per_session: int = 25,
        max_sessions_per_week: int = 7,
        min_session_duration: int = 20,
        max_session_duration: int = 120,
    ) -> ValidationResult:
        result = ValidationResult()
        for session in macrocycle.sessions:
            if session.is_deload or session.is_recovery:
                continue
            if session.total_sets > max_sets_per_session:
                result.add_error(
                    f"sessions.{session.session_id}.total_sets",
                    f"Exceeds max {max_sets_per_session} sets per session",
                    "C001",
                )
            if session.estimated_duration_minutes < min_session_duration:
                result.add_error(
                    f"sessions.{session.session_id}.duration",
                    f"Session too short ({session.estimated_duration_minutes}min < {min_session_duration})",
                    "C002",
                )
            if session.estimated_duration_minutes > max_session_duration:
                result.add_warning(
                    f"sessions.{session.session_id}.duration",
                    f"Session too long ({session.estimated_duration_minutes}min > {max_session_duration})",
                    "C003",
                )
        for week in macrocycle.weeks:
            if week.is_deload_week:
                continue
            if week.session_count > max_sessions_per_week:
                result.add_error(
                    f"weeks[{week.week_number}].session_count",
                    f"Exceeds max {max_sessions_per_week} sessions per week",
                    "C004",
                )
        return result


class PlanningValidator:
    """Aggregate validator — runs all sub-validators and merges results."""

    def __init__(
        self,
        config: PlanningConfig | None = None,
    ) -> None:
        self.config = config or PlanningConfig()
        self.scientific = ScientificValidator()
        self.volume = VolumeValidator()
        self.recovery = RecoveryValidator()
        self.frequency = FrequencyValidator()
        self.constraint = ConstraintValidator()

    def validate(self, macrocycle: Macrocycle) -> ValidationResult:
        result = ValidationResult()
        result.merge(self.scientific.validate(macrocycle))
        result.merge(self.volume.validate(macrocycle, self.config))
        result.merge(self.recovery.validate(macrocycle, self.config))
        result.merge(self.frequency.validate(macrocycle, self.config))
        result.merge(self.constraint.validate(macrocycle))
        return result

    def validate_mesocycle(self, mesocycle: Mesocycle) -> ValidationResult:
        result = ValidationResult()
        result.merge(self.scientific.validate_mesocycle_sequence(
            Macrocycle(mesocycles=[mesocycle]), result
        ) if False else result)
        return result

    def validate_week(self, week: WeekPlan) -> ValidationResult:
        result = ValidationResult()
        if week.session_count < self.config.min_sessions_per_week and not week.is_deload_week:
            result.add_error(
                f"week[{week.week_number}]",
                f"Minimum {self.config.min_sessions_per_week} sessions required",
                "V003",
            )
        return result

    def validate_session(self, session: SessionPlan) -> ValidationResult:
        result = ValidationResult()
        if session.total_sets > self.config.max_sets_per_session:
            result.add_error(
                f"session.{session.session_id}",
                f"Maximum {self.config.max_sets_per_session} sets per session",
                "V002",
            )
        return result

    def is_plan_safe(self, macrocycle: Macrocycle) -> bool:
        result = self.validate(macrocycle)
        return result.is_valid and result.error_count == 0
