"""ProgramValidator — validate workout program structure before import."""

from dataclasses import dataclass, field

from modules.workout_program.domain import WorkoutProgram


@dataclass
class ValidationError:
    field: str
    message: str
    day: str | None = None
    exercise: str | None = None


@dataclass
class ValidationResult:
    passed: bool = True
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, field: str, message: str, day: str | None = None, exercise: str | None = None):
        self.errors.append(ValidationError(field=field, message=message, day=day, exercise=exercise))
        self.passed = False

    def add_warning(self, message: str):
        self.warnings.append(message)


REP_RANGE_PATTERNS = (
    r"^\d+$",
    r"^\d+–\d+$",
    r"^\d+-\d+$",
)


def _looks_like_rep_range(value: str) -> bool:
    import re
    return any(re.match(pat, value.strip()) for pat in REP_RANGE_PATTERNS)


class ProgramValidator:
    def validate(self, program: WorkoutProgram) -> ValidationResult:
        result = ValidationResult()

        if not program.name or not program.name.strip():
            result.add_error("name", "Program name is required.")

        if not program.days:
            result.add_error("days", "Program must have at least one day.")
            return result

        seen_day_names: set[str] = set()

        for day in program.days:
            if not day.name or not day.name.strip():
                result.add_error(
                    "day_name",
                    "Day name is required.",
                    day=f"(day #{day.sort_order + 1})",
                )
                continue

            if day.name.strip().lower() in seen_day_names:
                result.add_error(
                    "day_name",
                    f"Duplicate day name: '{day.name}'.",
                    day=day.name,
                )
            seen_day_names.add(day.name.strip().lower())

            if not day.exercises:
                result.add_error(
                    "exercises",
                    f"Day '{day.name}' has no exercises.",
                    day=day.name,
                )
                continue

            seen_ex_names: set[str] = set()
            for ex in day.exercises:
                if not ex.name or not ex.name.strip():
                    result.add_error(
                        "exercise_name",
                        f"Exercise name is required in day '{day.name}'.",
                        day=day.name,
                    )
                    continue

                ex_lower = ex.name.strip().lower()
                if ex_lower in seen_ex_names:
                    result.add_error(
                        "duplicate_exercise",
                        f"Duplicate exercise '{ex.name}' in day '{day.name}'.",
                        day=day.name,
                        exercise=ex.name,
                    )
                seen_ex_names.add(ex_lower)

                if ex.target_sets < 1:
                    result.add_error(
                        "target_sets",
                        f"Exercise '{ex.name}' in day '{day.name}' has {ex.target_sets} sets (minimum 1).",
                        day=day.name,
                        exercise=ex.name,
                    )

                if not ex.target_reps or not _looks_like_rep_range(str(ex.target_reps)):
                    result.add_error(
                        "target_reps",
                        f"Exercise '{ex.name}' in day '{day.name}' has invalid rep range: '{ex.target_reps}'.",
                        day=day.name,
                        exercise=ex.name,
                    )

        return result
