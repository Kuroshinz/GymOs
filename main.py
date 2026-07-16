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
from shared.version import APP_VERSION, APP_NAME, APP_ORGANIZATION
from shared.helpers.logging import setup_production_logging
from PySide6.QtCore import QCoreApplication
from ui.design_system.theme import global_stylesheet
from ui.main_window import MainWindow
from ui.resources.icon import create_app_icon
from ui.splash.splash_screen import install_splash

logger = logging.getLogger(__name__)

from shared.helpers.resources import resource_path

if getattr(sys, "frozen", False):
    DB_DIR = os.path.expanduser("~/.gymos/data")
    os.makedirs(DB_DIR, exist_ok=True)
    DB_PATH = os.path.normpath(os.path.join(DB_DIR, "gymos.db"))
else:
    DB_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), "data", "gymos.db"))

CANONICAL_PROGRAM = resource_path(os.path.join("data", "program.json"))


def validate_startup_environment() -> None:
    """Validate user dirs, databases, and resource layouts, fallback if needed."""
    # 1. Check user directories
    user_dir = os.path.expanduser("~/.gymos")
    for sub in ("data", "crashes", "logs", "cache"):
        os.makedirs(os.path.join(user_dir, sub), exist_ok=True)
    
    # 2. Check write permissions
    test_file = os.path.join(user_dir, "cache", ".write_test")
    try:
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
    except Exception as e:
        logger.error("Startup validation: AppData cache directory not writable: %s", e)

    # 3. Writable database location directory
    db_dir = os.path.dirname(DB_PATH)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    # 4. Check canonical program exists, create stub if missing
    prog_dir = os.path.dirname(CANONICAL_PROGRAM)
    if prog_dir:
        os.makedirs(prog_dir, exist_ok=True)
    if not os.path.exists(CANONICAL_PROGRAM):
        logger.warning("Resource validation: program.json missing! Creating stub.")
        try:
            with open(CANONICAL_PROGRAM, "w", encoding="utf-8") as f:
                f.write('{"exercises": []}')
        except Exception as e:
            logger.error("Could not create stub program.json: %s", e)


def init_infrastructure(db_path: str = DB_PATH) -> None:
    validate_startup_environment()
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
    setup_production_logging()

    logger.info("GymOS %s starting up...", APP_VERSION)

    app = QApplication(sys.argv)
    QCoreApplication.setApplicationName(APP_NAME)
    QCoreApplication.setApplicationVersion(APP_VERSION)
    QCoreApplication.setOrganizationName(APP_ORGANIZATION)
    QCoreApplication.setOrganizationDomain("gymos.org")
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

    # Start non-blocking background update check
    import threading
    def bg_update_check():
        try:
            from shared.update.checker import check_for_updates
            res = check_for_updates()
            if res.has_update:
                logger.info("Background update check: Update available: v%s", res.remote_version)
        except Exception as e:
            logger.error("Background update check failed: %s", e)
    threading.Thread(target=bg_update_check, daemon=True).start()

    window.show()

    exit_code = app.exec()
    safe_shutdown()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
