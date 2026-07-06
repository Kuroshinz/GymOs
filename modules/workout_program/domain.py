"""Domain models for workout programs — pure data, no persistence."""

from dataclasses import dataclass, field


@dataclass
class ProgramExercise:
    name: str
    target_sets: int = 3
    target_reps: str = "10"
    muscle_group: str = ""
    exercise_id: str = ""
    sort_order: int = 0
    notes: str = ""


@dataclass
class ProgramDay:
    name: str
    sort_order: int = 0
    exercises: list[ProgramExercise] = field(default_factory=list)
    notes: str = ""


@dataclass
class DeloadWeek:
    frequency_weeks: int = 4
    type: str = "reduced_volume"
    description: str = ""


@dataclass
class ProgressionStrategy:
    primary: str = ""
    description: str = ""


@dataclass
class WorkoutProgram:
    name: str
    description: str = ""
    version: str = ""
    author: str = ""
    source_file: str = ""
    goal: str = "hypertrophy"
    experience_level: str = "intermediate"
    split: str = ""
    mesocycle_duration_weeks: int = 8
    deload_week: DeloadWeek | None = None
    progression_strategy: ProgressionStrategy | None = None
    priority_muscles: list[str] = field(default_factory=list)
    rules: list[str] = field(default_factory=list)
    days: list[ProgramDay] = field(default_factory=list)
