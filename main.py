#!/usr/bin/env python3
"""GymOS — Personal Hypertrophy Operating System (v0.1.0 MVP)"""

import sys
import os

from PySide6.QtWidgets import QApplication

from modules.workout.infrastructure.models import init_db
from modules.workout.infrastructure.repository import GymDatabase
from modules.workout_program.manager import ProgramManager
from modules.nutrition.infrastructure.repository import NutritionRepository
from modules.nutrition.services import NutritionService
from shared.events.event_bus import get_event_bus
from shared.events.subscribers.nutrition_subscriber import NutritionSubscriber
from modules.gymbrain.services.decision_engine import DecisionEngine
from ui.main_window import MainWindow


DB_PATH = os.path.join(os.path.dirname(__file__), "data", "gymos.db")
CANONICAL_PROGRAM = os.path.join(
    os.path.dirname(__file__), "data", "program.json"
)


def main() -> None:
    init_db(DB_PATH)
    db = GymDatabase(DB_PATH)
    prog_mgr = ProgramManager(DB_PATH)

    if prog_mgr.repository.count() == 0:
        if os.path.exists(CANONICAL_PROGRAM):
            prog_mgr.import_save_and_activate(CANONICAL_PROGRAM)
    elif prog_mgr.get_active_program() is None:
        programs = prog_mgr.list_programs()
        if programs:
            prog_mgr.switch_to_program(programs[0]["id"])

    # Nutrition wiring
    nutrition_repo = NutritionRepository(DB_PATH)
    event_bus = get_event_bus()
    nutrition_service = NutritionService(
        repository=nutrition_repo,
        db=db,
        event_bus=event_bus,
    )

    # Wire DecisionEngine with NutritionProvider
    engine = DecisionEngine.from_production(
        db=db,
        nutrition_provider=nutrition_service.provider,
    )

    # Wire NutritionSubscriber for cache invalidation
    NutritionSubscriber(bus=event_bus, decision_engine=engine)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow(
        db=db,
        prog_mgr=prog_mgr,
        nutrition_service=nutrition_service,
    )
    window.show()

    exit_code = app.exec()
    db.dispose()
    prog_mgr.dispose()
    nutrition_service.dispose()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
