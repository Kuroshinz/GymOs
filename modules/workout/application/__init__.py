"""Workout application service."""

from datetime import datetime
from typing import Optional

from modules.workout.domain import WorkoutSession


class WorkoutService:
    """Synchronous application service for workout operations."""

    def __init__(self, db) -> None:
        self._db = db

    def create_session(self, day_name: str, program_name: str = "PPL-UL",
                       exercise_names: list[str] | None = None,
                       target_sets_list: list[int] | None = None) -> WorkoutSession:
        """Create a new workout session."""
        from modules.workout.domain import SessionExercise, SessionSet

        names = exercise_names or []
        sets_counts = target_sets_list or [3] * len(names)

        exercises = []
        for i, name in enumerate(names):
            target = sets_counts[i] if i < len(sets_counts) else 3
            sets = [SessionSet(set_number=j + 1) for j in range(target)]
            exercises.append(SessionExercise(name=name, sets=sets, sort_order=i))

        session = WorkoutSession(
            day_name=day_name,
            program_name=program_name,
            exercises=exercises,
            started_at=datetime.now(),
        )
        return self._db.save_session(session)

    def complete_session(self, session_id: str) -> WorkoutSession:
        """Mark a workout session as completed."""
        session = self._db.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        session.completed_at = datetime.now()
        return self._db.save_session(session)

    def get_session(self, session_id: str) -> WorkoutSession | None:
        return self._db.get_session(session_id)

    def list_sessions(self, limit: int = 20, offset: int = 0) -> list[WorkoutSession]:
        return self._db.list_sessions(limit=limit, offset=offset)
