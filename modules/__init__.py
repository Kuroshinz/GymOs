# Only export what actually exists
from modules.workout import WorkoutSession, SessionExercise, SessionSet, WorkoutProgram, WorkoutDay, BodyWeight

__all__ = [
    "WorkoutSession",
    "SessionExercise",
    "SessionSet",
    "WorkoutProgram",
    "WorkoutDay",
    "BodyWeight",
]
