"""GymOS Main Window — sidebar navigation with stacked content views."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QLabel, QFrame,
)

from ui.dashboard import DashboardView
from ui.workout_selection_view import WorkoutSelectionView
from ui.workout_view import WorkoutView
from ui.progress_view import ProgressView
from ui.settings_view import SettingsView
from ui.pr_view import PRView
from ui.import_wizard import ImportWizard


PAGE_INDEX = {
    "dashboard": 0,
    "workout": 1,
    "progress": 2,
    "prs": 3,
    "settings": 4,
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
    def __init__(self, db, prog_mgr=None):
        super().__init__()
        self._db = db
        self._prog_mgr = prog_mgr
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

        self._dashboard_view = DashboardView(db=db, prog_mgr=prog_mgr)
        self._workout_selection_view = WorkoutSelectionView(db, prog_mgr)
        self._workout_view = WorkoutView(db, prog_mgr)
        self._progress_view = ProgressView(db)
        self._pr_view = PRView(db)
        self._settings_view = SettingsView(db, prog_mgr)

        self._content.addWidget(self._dashboard_view)       # 0
        self._content.addWidget(self._workout_selection_view)  # 1
        self._content.addWidget(self._progress_view)         # 2
        self._content.addWidget(self._pr_view)               # 3
        self._content.addWidget(self._settings_view)         # 4
        self._content.addWidget(self._workout_view)          # 5

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

        version = QLabel("v0.1.0 MVP")
        version.setStyleSheet("color: #475569; font-size: 11px; padding: 8px 12px;")
        layout.addWidget(version)

        return sidebar

    def _open_import_wizard(self):
        dialog = ImportWizard(self._prog_mgr, self)
        if dialog.exec() == ImportWizard.Done:
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
        elif index == PAGE_INDEX["prs"]:
            self._pr_view.refresh()
        elif index == PAGE_INDEX["settings"]:
            self._settings_view.refresh()

        self._content.setCurrentIndex(index)

    def _on_workout_selected(self, day_name: str):
        self._workout_view.load_day(day_name)
        self._content.setCurrentIndex(5)

    def _on_workout_saved(self):
        self._switch_to(PAGE_INDEX["dashboard"])
