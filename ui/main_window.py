"""GymOS Main Window — sidebar navigation with stacked content views."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QWizard,
)

from ui.dashboard import DashboardView
from ui.experience import ExperienceManager
from ui.experience.integration import integrate_with_command_center
from ui.import_wizard import ImportWizard
from ui.pr_view import PRView
from ui.prediction import PredictionDashboard, PredictionDashboardData
from ui.progress_view import ProgressView
from ui.recovery import RecoveryDashboard
from ui.settings_view import SettingsView
from ui.workout_selection_view import WorkoutSelectionView
from ui.workout_view import WorkoutView

PAGE_INDEX = {
    "dashboard": 0,
    "workout": 1,
    "progress": 2,
    "recovery": 3,
    "predictions": 4,
    "prs": 5,
    "settings": 6,
}


class SidebarButton(QPushButton):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94A3B8;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                text-align: left;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1E293B;
                color: #F1F5F9;
            }
            QPushButton[active="true"] {
                background-color: #1E293B;
                color: #818CF8;
                font-weight: 600;
            }
        """)


class MainWindow(QMainWindow):
    def __init__(self, db, prog_mgr=None, nutrition_service=None, recovery_service=None, prediction_service=None, experience=None):
        super().__init__()
        self._db = db
        self._prog_mgr = prog_mgr
        self._nutrition_service = nutrition_service
        self._recovery_service = recovery_service
        self._prediction_service = prediction_service
        self._recovery_dashboard = None
        self._prediction_dashboard = None
        self._experience = experience or ExperienceManager(self)
        self.setWindowTitle("GymOS")
        self.setMinimumSize(1024, 768)
        self.setStyleSheet("""
            QMainWindow { background-color: #0F172A; }
            QLabel { color: #F1F5F9; }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._nav_buttons: list[SidebarButton] = []

        sidebar = self._build_sidebar()
        main_layout.addWidget(sidebar)

        self._content = QStackedWidget()
        self._content.setStyleSheet("background-color: #0F172A;")
        main_layout.addWidget(self._content, 1)

        self._dashboard_view = DashboardView(db=db, prog_mgr=prog_mgr, nutrition_service=nutrition_service)
        self._workout_selection_view = WorkoutSelectionView(db, prog_mgr)
        self._workout_view = WorkoutView(db, prog_mgr)
        self._progress_view = ProgressView(db)
        self._recovery_dashboard = RecoveryDashboard() if recovery_service else None
        self._prediction_dashboard = PredictionDashboard() if prediction_service else None
        self._pr_view = PRView(db)
        self._settings_view = SettingsView(db, prog_mgr)

        self._content.addWidget(self._dashboard_view)           # 0
        self._content.addWidget(self._workout_selection_view)   # 1
        self._content.addWidget(self._progress_view)            # 2
        if self._recovery_dashboard:
            self._content.addWidget(self._recovery_dashboard)   # 3
        if self._prediction_dashboard:
            self._content.addWidget(self._prediction_dashboard)  # 4
        self._content.addWidget(self._pr_view)                  # 5
        self._content.addWidget(self._settings_view)            # 6
        self._content.addWidget(self._workout_view)             # 7

        self._dashboard_view.start_workout_clicked.connect(
            lambda: self._switch_to(PAGE_INDEX["workout"])
        )
        self._dashboard_view.view_all_prs_clicked.connect(
            lambda: self._switch_to(PAGE_INDEX["prs"])
        )
        self._dashboard_view.view_recommendations_clicked.connect(
            lambda: self._switch_to(PAGE_INDEX["progress"])
        )
        self._dashboard_view.weekly_review_clicked.connect(
            lambda: self._switch_to(PAGE_INDEX["progress"])
        )
        self._dashboard_view.log_weight_clicked.connect(
            lambda: self._switch_to(PAGE_INDEX["settings"])
        )
        self._dashboard_view.import_program_clicked.connect(
            lambda: self._open_import_wizard()
        )
        self._workout_selection_view.workout_selected.connect(self._on_workout_selected)
        self._workout_view.workout_saved.connect(self._on_workout_saved)
        self._workout_view.back_clicked.connect(
            lambda: self._switch_to(PAGE_INDEX["workout"])
        )

        self._experience.initialize()
        integrate_with_command_center(self._experience)
        self._experience.focus.register_sidebar(sidebar)

        self._switch_to(PAGE_INDEX["dashboard"])

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(
            "background-color: #0F172A; border-right: 1px solid #1E293B;"
        )

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(4)

        logo = QLabel("GymOS")
        logo.setStyleSheet(
            "font-size: 20px; font-weight: 700; color: #818CF8; padding: 8px 12px 20px 12px;"
        )
        layout.addWidget(logo)

        nav_items = [
            ("dashboard", "Dashboard"),
            ("workout", "Workout"),
            ("progress", "Progress"),
            ("recovery", "Recovery"),
            ("predictions", "Predictions"),
            ("prs", "Records"),
            ("settings", "Settings"),
        ]

        for page_key, label in nav_items:
            btn = SidebarButton(label)
            idx = PAGE_INDEX[page_key]
            btn.clicked.connect(lambda checked, i=idx: self._switch_to(i))
            self._nav_buttons.append(btn)
            layout.addWidget(btn)

        if self._prog_mgr:
            import_btn = SidebarButton("Import Program")
            import_btn.setStyleSheet(import_btn.styleSheet() + """
                QPushButton { color: #818CF8; font-size: 12px; border-top: 1px solid #1E293B; margin-top: 8px; padding-top: 12px; }
                QPushButton:hover { color: #6366F1; }
            """)
            import_btn.clicked.connect(self._open_import_wizard)
            layout.addWidget(import_btn)

        layout.addStretch()

        from shared.version import APP_VERSION
        version = QLabel(f"v{APP_VERSION}")
        version.setStyleSheet("color: #475569; font-size: 11px; padding: 8px 12px;")
        layout.addWidget(version)

        return sidebar

    def _open_import_wizard(self):
        dialog = ImportWizard(self._prog_mgr, self)
        if dialog.exec() == QWizard.Accepted:
            self._dashboard_view.refresh()
            self._workout_selection_view.refresh()

    def _switch_to(self, index: int):
        for i, btn in enumerate(self._nav_buttons):
            btn.setProperty("active", i == index)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        if index == PAGE_INDEX["dashboard"]:
            self._dashboard_view.refresh()
        elif index == PAGE_INDEX["workout"]:
            self._workout_selection_view.refresh()
        elif index == PAGE_INDEX["progress"]:
            self._progress_view.refresh()
        elif index == PAGE_INDEX["recovery"]:
            self._refresh_recovery()
        elif index == PAGE_INDEX["predictions"]:
            self._refresh_predictions()
        elif index == PAGE_INDEX["prs"]:
            self._pr_view.refresh()
        elif index == PAGE_INDEX["settings"]:
            self._settings_view.refresh()

        self._content.setCurrentIndex(index)

    def _on_workout_selected(self, day_name: str):
        self._workout_view.load_day(day_name)
        self._content.setCurrentIndex(7)

    def _refresh_predictions(self):
        if self._prediction_service and self._prediction_dashboard:
            from modules.prediction.presentation import PredictionFormatter
            result = self._prediction_service.generate_all_predictions()
            vm = PredictionFormatter.prediction_result_to_view_model(result)
            data = PredictionDashboardData(
                view_model=vm,
                has_data=len(result.predictions) > 0,
                result=result,
            )
            self._prediction_dashboard.refresh(data)

    def _refresh_recovery(self):
        if self._recovery_service and self._recovery_dashboard:
            svc = self._recovery_service
            snapshot = svc.get_snapshot()
            scores = svc.get_recent_scores(days=7)
            trend = svc.get_trend(days=14)
            weekly = svc.get_weekly_averages(weeks=4)
            active_deload = svc.get_active_deload()
            recs = svc.get_recommendations(days=1)

            level_str = ""
            if hasattr(snapshot, "readiness_level"):
                lvl = snapshot.readiness_level
                if hasattr(lvl, "value"):
                    level_str = lvl.value
                else:
                    level_str = str(lvl)

            from ui.recovery.recovery_dashboard import RecoveryDashboardData
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
        self._switch_to(PAGE_INDEX["dashboard"])
