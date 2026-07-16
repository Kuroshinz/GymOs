from __future__ import annotations

from typing import Any
from shared.interfaces import IRecoveryRepository, IProgressRepository, IWorkoutRepository

class SQLiteRecoveryRepository(IRecoveryRepository):
    """SQLite implementation of the recovery repository interface."""
    def __init__(self, db: Any) -> None:
        self._db = db


class SQLiteProgressRepository(IProgressRepository):
    """SQLite implementation of the training progress repository interface."""
    def __init__(self, db: Any) -> None:
        self._db = db

    def get_volume_by_day(self, days: int = 90) -> list[dict]:
        return self._db.get_volume_by_day(days=days)

    def get_body_weight_history(self, days: int = 90) -> list[Any]:
        return self._db.get_body_weight_history(days=days)

    def list_sessions(self, limit: int = 10) -> list[Any]:
        return self._db.list_sessions(limit=limit)

    def get_latest_body_weight(self) -> float | None:
        return self._db.get_latest_body_weight()


class SQLiteWorkoutRepository(IWorkoutRepository):
    """SQLite implementation of the workout repository interface."""
    def __init__(self, db: Any) -> None:
        self._db = db

    def get_program_days(self, program_name: str) -> list[Any]:
        return self._db.get_program_days(program_name)

    def get_last_session_for_exercise(self, exercise_name: str) -> Any:
        return self._db.get_last_session_for_exercise(exercise_name)

    def save_session(self, session: Any) -> Any:
        return self._db.save_session(session)

