#!/usr/bin/env python3
"""GymOS — Personal Hypertrophy Operating System"""

import logging
import os
import sys

from PySide6.QtWidgets import QApplication
from sqlalchemy import text

from modules.gymbrain.services.decision_engine import DecisionEngine
from modules.nutrition.infrastructure.repository import NutritionRepository
from modules.nutrition.services import NutritionService
from modules.prediction.application import PredictionService
from modules.prediction.infrastructure.repository import PredictionRepository
from modules.recovery.application import RecoveryService
from modules.recovery.infrastructure.repository import RecoveryRepository
from modules.workout.infrastructure.models import init_db
from modules.workout.infrastructure.repository import GymDatabase
from modules.workout_program.manager import ProgramManager
from shared.crash.handler import install_global_handler, register_cleanup, safe_shutdown
from shared.crash.recovery import show_recovery_dialog_if_needed
from shared.database.compatibility import all_compatible
from shared.database.engine import create_safe_engine, set_schema_version
from shared.events.event_bus import get_event_bus
from shared.events.subscribers.nutrition_subscriber import NutritionSubscriber
from shared.events.subscribers.recovery_subscriber import RecoverySubscriber
from shared.version import APP_VERSION
from ui.design_system.theme import global_stylesheet
from ui.main_window import MainWindow
from ui.resources.icon import create_app_icon
from ui.splash.splash_screen import install_splash

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "gymos.db")
CANONICAL_PROGRAM = os.path.join(
    os.path.dirname(__file__), "data", "program.json"
)


def init_infrastructure(db_path: str = DB_PATH) -> None:
    install_global_handler()
    show_recovery_dialog_if_needed()

    engine = create_safe_engine(db_path)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    if not all_compatible(engine):
        logger.warning("Database compatibility check failed — attempting migration")
        from scripts.migrate_db import migrate_upgrade, needs_migration
        if needs_migration(db_path):
            from scripts.backup.manager import backup_before_migration
            result = backup_before_migration(db_path)
            if result.success:
                logger.info("Pre-migration backup: %s", result.backup_path)
            migrate_upgrade(db_path)

    set_schema_version(engine)
    engine.dispose()


def run_onboarding() -> None:
    """Show first-launch wizard if needed, seed demo data if requested."""
    from ui.experience.welcome_wizard import WelcomeWizard, needs_onboarding

    if not needs_onboarding():
        return

    app = QApplication.instance()
    if app is None:
        return

    wizard = WelcomeWizard()

    def on_complete(name: str, goal: str, experience: str) -> None:
        if name:
            logger.info("User profile created: %s (%s, %s)", name, goal, experience)

    wizard.onboarding_complete.connect(on_complete)
    wizard.exec()


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    logger.info("GymOS %s starting up...", APP_VERSION)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setStyleSheet(global_stylesheet())
    app.aboutToQuit.connect(safe_shutdown)

    splash = install_splash()
    splash.advance("Initializing infrastructure...", 5)
    init_infrastructure()



    splash.advance("Initializing controller...", 80)
    from ui.shell.controller import ApplicationController
    controller = ApplicationController(DB_PATH)
    register_cleanup(controller.dispose)

    # Boot programs if empty
    if controller.prog_mgr.repository.count() == 0:
        if os.path.exists(CANONICAL_PROGRAM):
            controller.prog_mgr.import_save_and_activate(CANONICAL_PROGRAM)
    elif controller.prog_mgr.get_active_program() is None:
        programs = controller.prog_mgr.list_programs()
        if programs:
            controller.prog_mgr.switch_to_program(programs[0]["id"])

    NutritionSubscriber(bus=controller._event_bus, decision_engine=controller.decision_engine)
    RecoverySubscriber(bus=controller._event_bus, recovery_service=controller.recovery_service)

    splash.advance("Building interface...", 90)
    window = MainWindow(controller)

    app_icon = create_app_icon()
    app.setWindowIcon(app_icon)
    window.setWindowIcon(app_icon)

    splash.advance("Ready", 100)
    splash.finish(window)

    run_onboarding()

    window.show()

    exit_code = app.exec()
    safe_shutdown()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
