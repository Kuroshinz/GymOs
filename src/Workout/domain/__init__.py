from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Optional


class MuscleGroup(Enum):
    CHEST = auto()
    BACK = auto()
    SHOULDERS = auto()
    BICEPS = auto()
    TRICEPS = auto()
    LEGS = auto()
    GLUTES = auto()
    CORE = auto()
    FULL_BODY = auto()


class ExerciseType(Enum):
    STRENGTH = auto()
    HYPERTROPHY = auto()
    ENDURANCE = auto()
    FLEXIBILITY = auto()
    CARDIO = auto()


@dataclass
class Set:
    reps: int
    weight: float
    rpe: Optional[float] = None
    duration_seconds: Optional[int] = None
    completed: bool = False


@dataclass
class Exercise:
    name: str
    muscle_group: MuscleGroup
    exercise_type: ExerciseType
    sets: list[Set] = field(default_factory=list)
    notes: str = ""


@dataclass
class Workout:
    id: Optional[str] = None
    name: str = ""
    exercises: list[Exercise] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: str = ""

    @property
    def duration_minutes(self) -> float:
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds() / 60
        return 0.0

    @property
    def total_volume(self) -> float:
        return sum(
            s.weight * s.reps
            for ex in self.exercises
            for s in ex.sets
            if s.completed
        )

    @property
    def is_completed(self) -> bool:
        return self.completed_at is not None
