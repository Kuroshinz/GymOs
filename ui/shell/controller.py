from __future__ import annotations
from typing import Any

from modules.workout.infrastructure.repository import GymDatabase
from modules.workout_program.manager import ProgramManager
from modules.nutrition.infrastructure.repository import NutritionRepository
from modules.nutrition.services import NutritionService
from modules.recovery.infrastructure.repository import RecoveryRepository
from modules.recovery.application import RecoveryService
from modules.prediction.infrastructure.repository import PredictionRepository
from modules.prediction.application import PredictionService
from modules.gymbrain.services.decision_engine import DecisionEngine
from shared.events.event_bus import get_event_bus
from shared.database.repositories import SQLiteRecoveryRepository, SQLiteProgressRepository, SQLiteWorkoutRepository

class ApplicationController:
    """Composition Root and Controller for GymOS Desktop application.
    
    Instantiates database gateways, repositories, services, and shared providers.
    """

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        
        from modules.workout.infrastructure.models import init_db
        init_db(db_path)
        
        self._db = GymDatabase(db_path)
        self._prog_mgr = ProgramManager(db_path)
        
        self._event_bus = get_event_bus()
        
        self._nutrition_repo = NutritionRepository(db_path)
        self._nutrition_service = NutritionService(
            repository=self._nutrition_repo,
            db=self._db,
            event_bus=self._event_bus,
        )
        
        self._recovery_repo = RecoveryRepository(db_path)
        self._recovery_service = RecoveryService(
            repository=self._recovery_repo,
            db=self._db,
            event_bus=self._event_bus,
        )
        
        self._prediction_repo = PredictionRepository(db_path)
        self._prediction_service = PredictionService(
            repository=self._prediction_repo,
            db=self._db,
            event_bus=self._event_bus,
        )
        
        self._decision_engine = DecisionEngine.from_production(
            db=self._db,
            nutrition_provider=self._nutrition_service.provider,
            recovery_provider=self._recovery_service.provider,
        )
        
        # Instantiate repositories
        self._recovery_repository = SQLiteRecoveryRepository(self._db)
        self._progress_repository = SQLiteProgressRepository(self._db)
        self._workout_repository = SQLiteWorkoutRepository(self._db)

    @property
    def db(self) -> GymDatabase:
        return self._db

    @property
    def prog_mgr(self) -> ProgramManager:
        return self._prog_mgr

    @property
    def nutrition_service(self) -> NutritionService:
        return self._nutrition_service

    @property
    def recovery_service(self) -> RecoveryService:
        return self._recovery_service

    @property
    def prediction_service(self) -> PredictionService:
        return self._prediction_service

    @property
    def decision_engine(self) -> DecisionEngine:
        return self._decision_engine

    @property
    def recovery_repository(self) -> SQLiteRecoveryRepository:
        return self._recovery_repository

    @property
    def progress_repository(self) -> SQLiteProgressRepository:
        return self._progress_repository

    @property
    def workout_repository(self) -> SQLiteWorkoutRepository:
        return self._workout_repository

    def dispose(self) -> None:
        if hasattr(self._db, "dispose"):
            self._db.dispose()
        if hasattr(self._prog_mgr, "dispose"):
            self._prog_mgr.dispose()
        if hasattr(self._nutrition_service, "dispose"):
            self._nutrition_service.dispose()
        if hasattr(self._recovery_service, "dispose"):
            self._recovery_service.dispose()
        if hasattr(self._prediction_service, "dispose"):
            self._prediction_service.dispose()
