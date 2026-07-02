import sys, os
sys.path.insert(0, str(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFrame, QStackedWidget, QLabel, QSizePolicy, QScrollArea
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QTimer, Signal
from PySide6.QtGui import QFont, QIcon, QColor, QPalette, QAction

from src.ui.pages import (
    DashboardPage, WorkoutPage, ExercisePage, NutritionPage,
    WeightPage, PhysiquePage, AnalyticsPage, SettingsPage,
    PRPage, CalendarPage, AchievementsPage, RecoveryPage,
    MuscleHeatmapPage
)

NAV_ITEMS = [
    ("dashboard", "📊", "Dashboard"),
    ("workout", "💪", "Workout"),
    ("exercises", "🏋️", "Exercises"),
    ("nutrition", "🥩", "Nutrition"),
    ("weight", "⚖️", "Weight"),
    ("physique", "📸", "Physique"),
    ("pr", "🏆", "PRs"),
    ("heatmap", "🔥", "Heatmap"),
    ("recovery", "🔄", "Recovery"),
    ("calendar", "📅", "Calendar"),
    ("analytics", "📈", "Analytics"),
    ("achievements", "⭐", "Achievements"),
    ("settings", "⚙️", "Settings"),
]


SIDEBAR_STYLE = """
QFrame#sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(18, 18, 30, 1),
        stop:1 rgba(12, 12, 22, 1));
    border-right: 1px solid rgba(255,255,255,0.06);
}
"""

NAV_BTN_STYLE = """
QPushButton {
    background: transparent;
    border: none;
    border-radius: 10px;
    padding: 10px 14px;
    text-align: left;
    font-size: 13px;
    font-weight: 500;
    color: #888;
}
QPushButton:hover {
    background: rgba(124, 58, 237, 0.1);
    color: #ddd;
}
"""

NAV_ACTIVE_STYLE = """
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(124, 58, 237, 0.2),
        stop:1 rgba(124, 58, 237, 0.1));
    border: none;
    border-radius: 10px;
    padding: 10px 14px;
    text-align: left;
    font-size: 13px;
    font-weight: 600;
    color: #7c3aed;
}
QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 rgba(124, 58, 237, 0.3),
        stop:1 rgba(124, 58, 237, 0.15));
    color: #8b5cf6;
}
"""

CONTENT_STYLE = """
QFrame#content {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 rgba(10, 10, 20, 1),
        stop:1 rgba(5, 5, 15, 1));
}
"""


class GymOSMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GYM OS ULTIMATE")
        self.setMinimumSize(1280, 800)
        self.setStyleSheet("""
            QMainWindow { background: #0a0a14; }
            QScrollBar:vertical {
                background: transparent;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: rgba(124,58,237,0.3);
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = self._build_sidebar()
        main_layout.addWidget(self.sidebar)

        self.content = QStackedWidget()
        self.content.setObjectName("content")
        self.content.setStyleSheet(CONTENT_STYLE)
        main_layout.addWidget(self.content, 1)

        self._init_pages()
        self.navigate("dashboard")

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setStyleSheet(SIDEBAR_STYLE)
        sidebar.setFixedWidth(200)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 16, 10, 16)
        layout.setSpacing(2)

        logo = QLabel("🏋️ GYM OS")
        logo.setStyleSheet("""
            font-size: 20px;
            font-weight: 800;
            color: #ffffff;
            padding: 8px 4px 18px 8px;
            letter-spacing: -0.5px;
        """)
        layout.addWidget(logo)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("background: transparent; border: none;")

        nav_container = QWidget()
        nav_container.setStyleSheet("background: transparent;")
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(2)

        self.nav_buttons = {}
        for page_id, icon, label in NAV_ITEMS:
            btn = QPushButton(f"  {icon}  {label}")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(NAV_BTN_STYLE)
            btn.clicked.connect(lambda checked, pid=page_id: self.navigate(pid))
            nav_layout.addWidget(btn)
            self.nav_buttons[page_id] = btn

        nav_layout.addStretch()
        scroll.setWidget(nav_container)
        layout.addWidget(scroll, 1)

        version = QLabel("v1.0.0 · Gym OS Ultimate")
        version.setStyleSheet("font-size: 10px; color: #555; padding: 8px 4px;")
        version.setAlignment(Qt.AlignCenter)
        layout.addWidget(version)

        return sidebar

    def _init_pages(self):
        self.pages = {}
        self.pages["dashboard"] = DashboardPage()
        self.pages["workout"] = WorkoutPage()
        self.pages["exercises"] = ExercisePage()
        self.pages["nutrition"] = NutritionPage()
        self.pages["weight"] = WeightPage()
        self.pages["physique"] = PhysiquePage()
        self.pages["pr"] = PRPage()
        self.pages["heatmap"] = MuscleHeatmapPage()
        self.pages["recovery"] = RecoveryPage()
        self.pages["calendar"] = CalendarPage()
        self.pages["analytics"] = AnalyticsPage()
        self.pages["achievements"] = AchievementsPage()
        self.pages["settings"] = SettingsPage()

        for page in self.pages.values():
            self.content.addWidget(page)

    def navigate(self, page_id: str):
        for pid, btn in self.nav_buttons.items():
            btn.setStyleSheet(NAV_ACTIVE_STYLE if pid == page_id else NAV_BTN_STYLE)
        if page_id in self.pages:
            self.content.setCurrentWidget(self.pages[page_id])
            if hasattr(self.pages[page_id], "on_show"):
                self.pages[page_id].on_show()


def run():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(10, 10, 20))
    palette.setColor(QPalette.WindowText, QColor(224, 224, 224))
    palette.setColor(QPalette.Base, QColor(15, 15, 30))
    palette.setColor(QPalette.AlternateBase, QColor(20, 20, 35))
    palette.setColor(QPalette.ToolTipBase, QColor(30, 30, 50))
    palette.setColor(QPalette.ToolTipText, QColor(224, 224, 224))
    palette.setColor(QPalette.Text, QColor(224, 224, 224))
    palette.setColor(QPalette.Button, QColor(30, 30, 50))
    palette.setColor(QPalette.ButtonText, QColor(224, 224, 224))
    palette.setColor(QPalette.Highlight, QColor(124, 58, 237))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)

    font = QFont("Segoe UI", 10)
    font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font)

    window = GymOSMainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(run())
