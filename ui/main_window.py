"""GymOS Main Window — sidebar navigation with stacked content views."""

from PySide6.QtCore import QTimer, Qt
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
from ui.design_system.theme import global_stylesheet
from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.experience import ExperienceManager
from ui.experience.integration import integrate_with_command_center
from ui.import_wizard import ImportWizard
from ui.pr_view import PRView
from ui.prediction import PredictionDashboard, PredictionDashboardData
from ui.progress import ProgressExperience
from ui.recovery import RecoveryDashboard
from ui.settings import SettingsExperience
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


class SidebarButton(QPushButton):
    def __init__(self, text: str, tooltip: str = "", parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(48)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)
        if tooltip:
            self.setToolTip(tooltip)
        self._update_style()

    def _update_style(self) -> None:
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {_c.text_secondary};
                border: 1px solid transparent;
                border-radius: 8px;
                padding: 8px 16px;
                text-align: left;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {_c.surface_hover};
                color: {_c.text_primary};
            }}
            QPushButton:focus {{
                border-color: {_c.primary};
                background-color: {_c.surface_hover};
            }}
            QPushButton[active="true"] {{
                background-color: {_c.surface_hover};
                color: {_c.primary};
                font-weight: 600;
            }}
            QPushButton[active="true"]:focus {{
                border-color: {_c.primary_hover};
            }}
        """)

    def set_active(self, active: bool) -> None:
        self.setProperty("active", active)
        self.style().unpolish(self)
        self.style().polish(self)


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

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._nav_buttons: list[SidebarButton] = []

        sidebar = self._build_sidebar()
        main_layout.addWidget(sidebar)

        self._content = QStackedWidget()
        self._content.setAccessibleName("Content area")
        self._content.setStyleSheet(f"background-color: {_c.background};")
        main_layout.addWidget(self._content, 1)

        self._dashboard_view = DashboardView(db=db, prog_mgr=prog_mgr, nutrition_service=nutrition_service)
        self._workout_selection_view = WorkoutSelectionView(db, prog_mgr)
        self._workout_view = WorkoutView(db, prog_mgr)
        self._progress_view = ProgressExperience(db)
        self._recovery_dashboard = RecoveryDashboard() if recovery_service else None
        self._prediction_dashboard = PredictionDashboard() if prediction_service else None
        self._pr_view = PRView(db)
        self._settings_view = SettingsExperience(db, prog_mgr)

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

        a11y = self._experience.accessibility
        a11y.high_contrast_changed.connect(self._on_high_contrast_changed)

        last_sidebar = self._nav_buttons[-1] if self._nav_buttons else sidebar
        self.setTabOrder(last_sidebar, self._content)

        self._switch_to(PAGE_INDEX["dashboard"])

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet(
            f"background-color: {_c.surface}; border-right: 1px solid {_c.border};"
        )

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 20, 12, 20)
        layout.setSpacing(4)

        logo = QLabel("GymOS")
        logo.setAccessibleName("Application logo")
        logo.setStyleSheet(
            f"font-size: 20px; font-weight: 700; color: {_c.primary}; padding: 8px 12px 20px 12px;"
        )
        layout.addWidget(logo)

        nav_items = [
            ("dashboard", "Dashboard", "View your training overview and quick actions"),
            ("workout", "Workout", "Select and start a workout session"),
            ("progress", "Progress", "View your training progress charts"),
            ("recovery", "Recovery", "Check recovery status and readiness"),
            ("predictions", "Predictions", "View training predictions and forecasts"),
            ("prs", "Records", "Browse your personal records"),
            ("settings", "Settings", "Configure application preferences"),
        ]

        prev_btn: QPushButton | None = None
        for page_key, label, tip in nav_items:
            btn = SidebarButton(label, tooltip=tip)
            btn.setAccessibleName(f"Navigate to {label}")
            idx = PAGE_INDEX[page_key]
            btn.clicked.connect(lambda checked, i=idx: self._switch_to(i))
            self._nav_buttons.append(btn)
            layout.addWidget(btn)
            if prev_btn:
                self.setTabOrder(prev_btn, btn)
            prev_btn = btn

        if self._prog_mgr:
            import_btn = SidebarButton("Import Program", tooltip="Import a workout program from a JSON file")
            import_btn.setAccessibleName("Import workout program")
            import_btn.setStyleSheet(import_btn.styleSheet() + f"""
                QPushButton {{ color: {_c.primary}; font-size: 12px; border-top: 1px solid {_c.border}; margin-top: 8px; padding-top: 12px; }}
                QPushButton:hover {{ color: {_c.primary_hover}; }}
            """)
            import_btn.clicked.connect(self._open_import_wizard)
            layout.addWidget(import_btn)
            if prev_btn:
                self.setTabOrder(prev_btn, import_btn)
            prev_btn = import_btn

        layout.addStretch()

        from shared.version import APP_VERSION
        version = QLabel(f"v{APP_VERSION}")
        version.setAccessibleName(f"GymOS version {APP_VERSION}")
        version.setStyleSheet(f"color: {_c.text_disabled}; font-size: 11px; padding: 8px 12px;")
        layout.addWidget(version)

        return sidebar

    def _open_import_wizard(self):
        dialog = ImportWizard(self._prog_mgr, self)
        if dialog.exec() == QWizard.Accepted:
            self._prediction_cache = None
            self._dashboard_cache_time = 0.0
            self._dashboard_view.refresh()
            self._workout_selection_view.refresh()

    def _on_high_contrast_changed(self, enabled: bool) -> None:
        scheme = ColorScheme.HIGH_CONTRAST if enabled else ColorScheme.DARK
        colors = global_stylesheet(scheme)
        self.setStyleSheet(colors)

    def _switch_to(self, index: int):
        for i, btn in enumerate(self._nav_buttons):
            btn.set_active(i == index)

        if index == PAGE_INDEX["dashboard"]:
            import time
            now = time.time()
            if now - self._dashboard_cache_time > 30:
                self._dashboard_cache_time = now
                QTimer.singleShot(0, self._dashboard_view.refresh)
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
        if not self._prediction_service or not self._prediction_dashboard:
            return
        import time
        now = time.time()
        if self._prediction_cache is not None and now - self._prediction_cache_time < 60:
            self._prediction_dashboard.refresh(self._prediction_cache)
            return
        QTimer.singleShot(0, self._do_refresh_predictions)

    def _do_refresh_predictions(self):
        if not self._prediction_service or not self._prediction_dashboard:
            return
        import time
        from modules.prediction.presentation import PredictionFormatter
        result = self._prediction_service.generate_all_predictions()
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
                level_str = lvl.value if hasattr(lvl, "value") else str(lvl)

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
        self._prediction_cache = None
        self._dashboard_cache_time = 0.0
        self._switch_to(PAGE_INDEX["dashboard"])
