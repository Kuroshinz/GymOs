from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QMainWindow,
    QWizard,
)

from ui.archive.prediction_dashboard import PredictionDashboard, PredictionDashboardData
from ui.archive.recovery_dashboard import RecoveryDashboard
from ui.dashboard import DashboardView
from ui.design_system.theme import global_stylesheet
from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.dialogs.set_goal_dialog import SetGoalDialog
from ui.experience import ExperienceManager, MotionService
from ui.experience.integration import integrate_with_command_center
from ui.import_wizard import ImportWizard
from ui.pr_view import PRView
from ui.progress import ProgressExperience
from ui.settings import SettingsExperience
from ui.shell import AppShell
from ui.workout_selection_view import WorkoutSelectionView
from ui.workout_view import WorkoutView

_c = color_from_scheme(ColorScheme.DARK)

PAGE_INDEX = {
    "dashboard": 0,
    "workout": 1,
    "progress": 2,
    "recovery": 3,
    "predictions": 4,
    "prs": 5,
    "settings": 6,
}


class MainWindow(QMainWindow):
    def __init__(self, db_or_controller: Any, prog_mgr=None, nutrition_service=None, recovery_service=None, prediction_service=None, experience=None):
        super().__init__()
        
        # Resolve controller with backward compatibility
        from ui.shell.controller import ApplicationController
        if isinstance(db_or_controller, ApplicationController):
            self._controller = db_or_controller
        else:
            class LegacyControllerAdapter:
                def __init__(self, db, pm, ns, rs, ps):
                    self.db = db
                    self.prog_mgr = pm
                    self.nutrition_service = ns
                    self.recovery_service = rs
                    self.prediction_service = ps
                    from shared.database.repositories import SQLiteProgressRepository
                    self.progress_repository = SQLiteProgressRepository(db)
                    
                    from modules.gymbrain.services.decision_engine import DecisionEngine
                    self.decision_engine = DecisionEngine.from_production(
                        db=db,
                        nutrition_provider=ns.provider if ns else None,
                        recovery_provider=rs.provider if rs else None,
                    )
            self._controller = LegacyControllerAdapter(
                db_or_controller, prog_mgr, nutrition_service, recovery_service, prediction_service
            )

        self._recovery_dashboard = None
        self._prediction_dashboard = None
        self._experience = experience or ExperienceManager(self)
        self._prediction_cache: PredictionDashboardData | None = None
        self._prediction_cache_time: float = 0.0
        self._dashboard_cache_time: float = 0.0
        self.setWindowTitle("GymOS")
        self.setAccessibleName("GymOS Main Window")
        self.setMinimumSize(1024, 768)
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {_c.background}; }}
            QLabel {{ color: {_c.text_primary}; }}
        """)

        self._motion = MotionService(self._experience.animation, self._experience.accessibility, self)
        self._shell = AppShell(motion=self._motion, parent=self)
        self.setCentralWidget(self._shell)
        self._sidebar = self._shell.sidebar

        from ui.desktop_integration import DesktopIntegrationManager
        self._desktop_integration = DesktopIntegrationManager(self)

        # Instantiate views via controller dependencies
        self._dashboard_view = DashboardView(
            db=self._controller.db,
            prog_mgr=self._controller.prog_mgr,
            nutrition_service=self._controller.nutrition_service
        )
        self._workout_selection_view = WorkoutSelectionView(self._controller.db, self._controller.prog_mgr)
        self._workout_view = WorkoutView(
            self._controller.db,
            self._controller.prog_mgr,
            recovery_service=self._controller.recovery_service
        )
        self._progress_view = ProgressExperience(self._controller.progress_repository)
        self._recovery_dashboard = RecoveryDashboard() if self._controller.recovery_service else None
        self._prediction_dashboard = PredictionDashboard() if self._controller.prediction_service else None
        self._pr_view = PRView(self._controller.db)
        self._settings_view = SettingsExperience(
            self._controller.db,
            self._controller.prog_mgr,
            recovery_service=self._controller.recovery_service
        )

        from ui.experience.weekly_review_view import WeeklyReviewView
        self._weekly_review_view = WeeklyReviewView(
            db=self._controller.db,
            decision_engine=self._controller.decision_engine
        )

        self._shell.add_page(self._dashboard_view, "dashboard")
        self._shell.add_page(self._workout_selection_view, "workout")
        self._shell.add_page(self._progress_view, "progress")
        if self._recovery_dashboard:
            self._shell.add_page(self._recovery_dashboard, "recovery")
        if self._prediction_dashboard:
            self._shell.add_page(self._prediction_dashboard, "predictions")
        self._shell.add_page(self._pr_view, "prs")
        self._shell.add_page(self._settings_view, "settings")
        self._shell.add_page(self._workout_view, "workout_detail")
        self._shell.add_page(self._weekly_review_view, "weekly_review")

        self._shell.page_switched.connect(self._on_page_switched)

        self._dashboard_view.start_workout_clicked.connect(
            lambda: self._shell.switch_to("workout", "page")
        )
        self._dashboard_view.view_all_prs_clicked.connect(
            lambda: self._shell.switch_to("prs", "page")
        )
        self._dashboard_view.view_recommendations_clicked.connect(
            lambda: self._shell.switch_to("progress", "page")
        )
        self._dashboard_view.weekly_review_clicked.connect(
            lambda: self._shell.switch_to("weekly_review", "page")
        )
        self._weekly_review_view.start_training_requested.connect(
            lambda: self._shell.switch_to("workout", "page")
        )
        self._dashboard_view.log_weight_clicked.connect(
            lambda: self._shell.switch_to("settings", "page")
        )
        self._dashboard_view.set_goal_clicked.connect(
            lambda: self._open_set_goal_dialog()
        )
        self._dashboard_view.import_program_clicked.connect(
            lambda: self._open_import_wizard()
        )
        self._workout_selection_view.workout_selected.connect(self._on_workout_selected)
        self._workout_view.workout_saved.connect(self._on_workout_saved)
        self._workout_view.back_clicked.connect(
            lambda: self._shell.switch_to("workout", "page")
        )

        self._experience.initialize()
        integrate_with_command_center(self._experience)
        self._experience.focus.register_sidebar(self._shell.sidebar)

        a11y = self._experience.accessibility
        a11y.high_contrast_changed.connect(self._on_high_contrast_changed)

        self._shell.switch_to("dashboard", "startup")

    def _on_page_switched(self, page_id: str, source: str) -> None:
        if page_id == "dashboard":
            import time
            now = time.time()
            if now - self._dashboard_cache_time > 30:
                self._dashboard_cache_time = now
                QTimer.singleShot(0, self._dashboard_view.refresh)
        elif page_id == "workout":
            self._workout_selection_view.refresh()
        elif page_id == "progress":
            self._progress_view.refresh()
        elif page_id == "weekly_review":
            self._weekly_review_view.refresh()
        elif page_id == "recovery":
            self._refresh_recovery()
        elif page_id == "predictions":
            self._refresh_predictions()
        elif page_id == "prs":
            self._pr_view.refresh()
        elif page_id == "settings":
            self._settings_view.refresh()

    def _open_set_goal_dialog(self) -> None:
        """Open the Set Goal dialog and persist the user's target."""
        # Pre-fill with current weight from dashboard data
        current_weight = 70.0
        try:
            last_data = self._dashboard_view.controller().last_data
            current_weight = getattr(last_data, "goal_progress_weight", 70.0) or 70.0
        except Exception:
            pass

        dialog = SetGoalDialog(current_weight=current_weight, parent=self)
        dialog.goal_set.connect(self._on_goal_set)
        dialog.exec()

    def _on_goal_set(self, target_weight_kg: float, target_calorie_surplus: int) -> None:
        """Handle goal being set: persist via controller and refresh."""
        try:
            self._dashboard_view.controller().set_goal(
                target_weight_kg=target_weight_kg,
                target_calorie_surplus=target_calorie_surplus,
            )
            self._dashboard_cache_time = 0.0
        except Exception:
            pass

    def _open_import_wizard(self):
        dialog = ImportWizard(self._controller.prog_mgr, self)
        if dialog.exec() == QWizard.Accepted:
            self._prediction_cache = None
            self._dashboard_cache_time = 0.0
            self._dashboard_view.refresh()
            self._workout_selection_view.refresh()

    def _on_high_contrast_changed(self, enabled: bool) -> None:
        scheme = ColorScheme.HIGH_CONTRAST if enabled else ColorScheme.DARK
        colors = global_stylesheet(scheme)
        self.setStyleSheet(colors)

    def _on_workout_selected(self, day_name: str):
        self._workout_view.load_day(day_name)
        self._shell.switch_to("workout_detail", "page")

    def _refresh_predictions(self):
        if not self._controller.prediction_service or not self._prediction_dashboard:
            return
        import time
        now = time.time()
        if self._prediction_cache is not None and now - self._prediction_cache_time < 60:
            self._prediction_dashboard.refresh(self._prediction_cache)
            return
        QTimer.singleShot(0, self._do_refresh_predictions)

    def _do_refresh_predictions(self):
        if not self._controller.prediction_service or not self._prediction_dashboard:
            return
        import time

        from modules.prediction.presentation import PredictionFormatter
        result = self._controller.prediction_service.generate_all_predictions()
        vm = PredictionFormatter.prediction_result_to_view_model(result)
        data = PredictionDashboardData(
            view_model=vm,
            has_data=len(result.predictions) > 0,
            result=result,
        )
        self._prediction_cache = data
        self._prediction_cache_time = time.time()
        self._prediction_dashboard.refresh(data)

    def _refresh_recovery(self):
        if self._controller.recovery_service and self._recovery_dashboard:
            svc = self._controller.recovery_service
            snapshot = svc.get_snapshot()
            scores = svc.get_recent_scores(days=7)
            trend = svc.get_trend(days=14)
            weekly = svc.get_weekly_averages(weeks=4)
            active_deload = svc.get_active_deload()
            recs = svc.get_recommendations(days=1)

            level_str = ""
            if hasattr(snapshot, "readiness_level"):
                lvl = snapshot.readiness_level
                level_str = lvl.value if hasattr(lvl, "value") else str(lvl)

            from ui.archive.recovery_dashboard import RecoveryDashboardData
            data = RecoveryDashboardData(
                recovery_score=snapshot.recovery_score if hasattr(snapshot, "recovery_score") else 0.0,
                recovery_level=level_str,
                recovery_flags=snapshot.flags if hasattr(snapshot, "flags") else [],
                recovery_sleep_score=snapshot.sleep_score if hasattr(snapshot, "sleep_score") else 0.0,
                recovery_stress_score=snapshot.stress_score if hasattr(snapshot, "stress_score") else 0.0,
                recovery_fatigue_score=snapshot.fatigue_score if hasattr(snapshot, "fatigue_score") else 0.0,
                recovery_trend=trend if hasattr(trend, "direction") else None,
                recovery_active_deload=active_deload,
                recovery_scores=scores,
                recovery_scores_count=len(scores),
                recovery_weekly=weekly,
                recovery_action=recs[0].message if recs and hasattr(recs[0], "message") else "",
            )
            self._recovery_dashboard.refresh(data)

    def _on_workout_saved(self):
        self._prediction_cache = None
        self._dashboard_cache_time = 0.0
        self._shell.switch_to("dashboard", "page")

    def closeEvent(self, event) -> None:
        """Handle application close event by hiding to tray instead of quitting."""
        if hasattr(self, "_desktop_integration") and self._desktop_integration._tray_icon is not None and self._desktop_integration._tray_icon.isVisible():
            self.hide()
            event.ignore()
            # Send a notification on first hide
            from PySide6.QtWidgets import QSystemTrayIcon
            self._desktop_integration.send_notification(
                "GymOS",
                "GymOS is still running in the system tray.",
                icon_type=QSystemTrayIcon.MessageIcon.Information
            )
        else:
            event.accept()
