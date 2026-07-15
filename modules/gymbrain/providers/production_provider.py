"""Production DataProvider — real repository-backed implementation.

Wires GymDatabase, knowledge repositories, and workout engines
into the DataProvider interface consumed by GymBrain.

All error handling is inherited from TrainingDataProvider via the
``@safe`` decorator — no manual try/except blocks.
"""

from __future__ import annotations

from typing import Any

from modules.gymbrain.providers.training_provider import TrainingDataProvider
from modules.workout.infrastructure.repository import GymDatabase


class ProductionDataProvider(TrainingDataProvider):
    """DataProvider backed by a real GymDatabase and knowledge repositories.

    All exercise/muscle lookups go through ExerciseRepository/MuscleRepository
    (loaded from knowledge YAML files). All session data goes through GymDatabase
    (the SQLite training log). Rule evaluation never touches infrastructure directly.

    Error handling is standardized via the ``@safe`` decorator inherited from
    TrainingDataProvider — no manual try/except anywhere in this class.
    """

    def __init__(
        self,
        db: GymDatabase,
        exercise_repo: Any = None,
        muscle_repo: Any = None,
        program_repo: Any = None,
        knowledge_service: Any = None,
        volume_engine: Any = None,
        pr_engine: Any = None,
        recovery_engine: Any = None,
        progression_engine: Any = None,
        nutrition_provider: Any = None,
    ) -> None:
        super().__init__(
            exercise_repo=exercise_repo,
            muscle_repo=muscle_repo,
            program_repo=program_repo,
            knowledge_service=knowledge_service,
            db=db,
            volume_engine=volume_engine,
            pr_engine=pr_engine,
            recovery_engine=recovery_engine,
            progression_engine=progression_engine,
            nutrition_provider=nutrition_provider,
        )
        self._db = db

    @classmethod
    def from_production(
        cls,
        db: GymDatabase,
        knowledge_service: Any = None,
        volume_engine: Any = None,
        pr_engine: Any = None,
        recovery_engine: Any = None,
        progression_engine: Any = None,
        exercise_repo: Any = None,
        muscle_repo: Any = None,
        program_repo: Any = None,
        nutrition_provider: Any = None,
        recovery_provider: Any = None,
        cache: Any = None,
    ) -> ProductionDataProvider:
        """Build a fully-wired ProductionDataProvider for production use.

        Accepts a ``GymDatabase`` instance and optional engine/repository overrides.
        When engines are omitted they are auto-created from the db.

        Usage::

            from modules.workout.infrastructure.repository import GymDatabase
            provider = ProductionDataProvider.from_production(
                db=GymDatabase("data/gymos.db")
            )
        """
        from modules.workout.application.pr_engine import PREngine
        from modules.workout.application.progression_engine import ProgressionEngine
        from modules.workout.application.recovery_engine import RecoveryEngine

        pr_engine = pr_engine or PREngine(db)
        recovery_engine = recovery_engine or RecoveryEngine(db)
        progression_engine = progression_engine or ProgressionEngine(db)

        provider = cls(
            db=db,
            exercise_repo=exercise_repo,
            muscle_repo=muscle_repo,
            program_repo=program_repo,
            knowledge_service=knowledge_service,
            volume_engine=volume_engine,
            pr_engine=pr_engine,
            recovery_engine=recovery_engine,
            progression_engine=progression_engine,
            nutrition_provider=nutrition_provider,
        )
        if recovery_provider:
            provider.recovery_provider = recovery_provider
        return provider
