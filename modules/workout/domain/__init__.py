"""GymOS workout domain entities."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class SessionSet:
    """A single completed set within a workout session."""

    set_number: int
    weight_kg: float = 0.0
    reps: int = 0
    rir: int | None = None  # Reps in Reserve (1-5)
    completed: bool = True


@dataclass
class SessionExercise:
    """An exercise logged during a workout session."""

    name: str
    sets: list[SessionSet] = field(default_factory=list)
    sort_order: int = 0
    notes: str = ""

    @property
    def total_volume(self) -> float:
        return sum(s.weight_kg * s.reps for s in self.sets if s.completed)

    @property
    def best_set(self) -> SessionSet | None:
        if not self.sets:
            return None
        return max(
            (s for s in self.sets if s.completed and s.reps > 0),
            key=lambda s: s.weight_kg * s.reps,
            default=None,
        )


@dataclass
class WorkoutSession:
    """A completed workout session."""

    id: str | None = None
    day_name: str = ""
    program_name: str = "PPL-UL"
    exercises: list[SessionExercise] = field(default_factory=list)
    started_at: datetime | None = None
    completed_at: datetime | None = None
    notes: str = ""

    @property
    def duration_minutes(self) -> float:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds() / 60
        return 0.0

    @property
    def total_volume(self) -> float:
        return sum(ex.total_volume for ex in self.exercises)

    @property
    def is_completed(self) -> bool:
        return self.completed_at is not None

    @property
    def completed_exercises(self) -> list[SessionExercise]:
        return [ex for ex in self.exercises if any(s.completed for s in ex.sets)]

    @property
    def completed_sets_count(self) -> int:
        return sum(1 for ex in self.exercises for s in ex.sets if s.completed)


@dataclass
class WorkoutDay:
    """A template day within a workout program."""

    id: str | None = None
    name: str = ""
    sort_order: int = 0
    exercise_names: list[str] = field(default_factory=list)
    target_sets: list[int] = field(default_factory=list)
    target_reps: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class WorkoutProgram:
    """A workout program containing days."""

    id: str | None = None
    name: str = ""
    description: str = ""
    days: list[WorkoutDay] = field(default_factory=list)


@dataclass
class BodyWeight:
    """Daily body weight log."""

    id: str | None = None
    date: str = ""
    weight_kg: float = 0.0
    notes: str = ""


@dataclass
class PreviousSessionData:
    """Previous session info for comparison display."""

    exercise_name: str
    sets: list[dict] = field(default_factory=list)  # [{weight, reps, rir}]
    date: str | None = None
