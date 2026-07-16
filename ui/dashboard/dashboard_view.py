"""Dashboard View — thin orchestration layer over extracted widgets.

External API is backward-compatible:
  - Constructor: DashboardView(db, prog_mgr, nutrition_service, controller, motion)
  - Methods: refresh(), controller(), set_motion_service(motion)
  - Signals: start_workout_clicked, view_all_prs_clicked, weekly_review_clicked,
             view_recommendations_clicked, log_weight_clicked, import_program_clicked, set_goal_clicked

Widgets are built in _build_ui and updated in _on_data_updated.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QGridLayout, QVBoxLayout, QWidget, QLabel, QProgressBar

from ui.dashboard.dashboard_controller import DashboardController
from ui.dashboard.dashboard_models import DashboardData
from ui.dashboard.dashboard_widgets.coach_widget import CoachPredictionsWidget
from ui.dashboard.dashboard_widgets.hero_widget import HeroWidget
from ui.dashboard.dashboard_widgets.mission_widget import MissionRecoveryWidget
from ui.dashboard.dashboard_widgets.progress_widget import ProgressWidget
from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.elevation import apply_elevation
from ui.design_system.layout import ScrollContainer
from ui.experience.motion_service import MotionService


class RecoveryCard(QFrame):
    """Compact Recovery Overview dashboard card."""
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("RecoveryCard")
        self.setStyleSheet(
            """
            QFrame#RecoveryCard {
                background-color: rgba(20, 21, 38, 0.65);
                border-radius: 16px;
                border: 1px solid rgba(255, 255, 255, 0.05);
            }
        """
        )
        apply_elevation(self, 1, is_dark=True, bg_color=color_from_scheme(ColorScheme.DARK).surface)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(12)
        
        # Title
        colors = color_from_scheme(ColorScheme.DARK)
        self._title = QLabel("RECOVERY OVERVIEW")
        self._title.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 10px; font-weight: 700; "
            f"letter-spacing: 1px; background: transparent;"
        )
        main_layout.addWidget(self._title)
        
        # Horizontal layout of drivers
        drivers_layout = QHBoxLayout()
        drivers_layout.setContentsMargins(0, 4, 0, 4)
        drivers_layout.setSpacing(16)
        
        # Sleep
        sleep_layout = QVBoxLayout()
        sleep_layout.setSpacing(2)
        self._sleep_val = QLabel("7.5h")
        self._sleep_val.setAlignment(Qt.AlignCenter)
        self._sleep_val.setStyleSheet(f"color: {colors.text_primary}; font-size: 16px; font-weight: 700; background: transparent;")
        self._sleep_lbl = QLabel("Sleep (Good)")
        self._sleep_lbl.setAlignment(Qt.AlignCenter)
        self._sleep_lbl.setStyleSheet(f"color: {colors.text_secondary}; font-size: 11px; background: transparent;")
        sleep_layout.addWidget(self._sleep_val)
        sleep_layout.addWidget(self._sleep_lbl)
        drivers_layout.addLayout(sleep_layout)
        
        # Stress
        stress_layout = QVBoxLayout()
        stress_layout.setSpacing(2)
        self._stress_val = QLabel("Low")
        self._stress_val.setAlignment(Qt.AlignCenter)
        self._stress_val.setStyleSheet(f"color: {colors.text_primary}; font-size: 16px; font-weight: 700; background: transparent;")
        self._stress_lbl = QLabel("Stress (Optimal)")
        self._stress_lbl.setAlignment(Qt.AlignCenter)
        self._stress_lbl.setStyleSheet(f"color: {colors.text_secondary}; font-size: 11px; background: transparent;")
        stress_layout.addWidget(self._stress_val)
        stress_layout.addWidget(self._stress_lbl)
        drivers_layout.addLayout(stress_layout)
        
        # HRV
        hrv_layout = QVBoxLayout()
        hrv_layout.setSpacing(2)
        self._hrv_val = QLabel("72 ms")
        self._hrv_val.setAlignment(Qt.AlignCenter)
        self._hrv_val.setStyleSheet(f"color: {colors.text_primary}; font-size: 16px; font-weight: 700; background: transparent;")
        self._hrv_lbl = QLabel("HRV (Optimal)")
        self._hrv_lbl.setAlignment(Qt.AlignCenter)
        self._hrv_lbl.setStyleSheet(f"color: {colors.text_secondary}; font-size: 11px; background: transparent;")
        hrv_layout.addWidget(self._hrv_val)
        hrv_layout.addWidget(self._hrv_lbl)
        drivers_layout.addLayout(hrv_layout)
        
        main_layout.addLayout(drivers_layout)
        
        # Progress/Score bar
        self._score_bar = QProgressBar()
        self._score_bar.setFixedHeight(8)
        self._score_bar.setRange(0, 100)
        self._score_bar.setValue(92)
        self._score_bar.setTextVisible(False)
        self._score_bar.setStyleSheet(
            f"""
            QProgressBar {{
                background-color: rgba(255, 255, 255, 0.05);
                border: none;
                border-radius: 4px;
            }}
            QProgressBar::chunk {{
                background-color: {colors.success};
                border-radius: 4px;
            }}
        """
        )
        
        self._score_lbl = QLabel("Recovery Score: 92%")
        self._score_lbl.setStyleSheet(f"color: {colors.text_secondary}; font-size: 11px; font-weight: 600; background: transparent;")
        
        main_layout.addWidget(self._score_lbl)
        main_layout.addWidget(self._score_bar)
        
    def update_data(self, data: DashboardData) -> None:
        colors = color_from_scheme(ColorScheme.DARK)
        score = getattr(data, "recovery_score", 0.0) or 0.0
        self._score_bar.setValue(int(score))
        self._score_lbl.setText(f"Recovery Score: {int(score)}%")
        
        status = getattr(data, "recovery_status", None)
        if status:
            if hasattr(status, "sleep_duration") and getattr(status, "sleep_duration"):
                self._sleep_val.setText(f"{getattr(status, 'sleep_duration'):.1f}h")
            if hasattr(status, "hrv") and getattr(status, "hrv"):
                self._hrv_val.setText(f"{getattr(status, 'hrv')} ms")
            if hasattr(status, "stress_level") and getattr(status, "stress_level"):
                self._stress_val.setText(str(getattr(status, "stress_level")).capitalize())

        if score < 50:
            self._score_bar.setStyleSheet(
                f"QProgressBar {{ background-color: rgba(255, 255, 255, 0.05); border: none; border-radius: 4px; }}"
                f"QProgressBar::chunk {{ background-color: {colors.error}; border-radius: 4px; }}"
            )
        elif score < 75:
            self._score_bar.setStyleSheet(
                f"QProgressBar {{ background-color: rgba(255, 255, 255, 0.05); border: none; border-radius: 4px; }}"
                f"QProgressBar::chunk {{ background-color: {colors.warning}; border-radius: 4px; }}"
            )
        else:
            self._score_bar.setStyleSheet(
                f"QProgressBar {{ background-color: rgba(255, 255, 255, 0.05); border: none; border-radius: 4px; }}"
                f"QProgressBar::chunk {{ background-color: {colors.success}; border-radius: 4px; }}"
            )


class InsightsCard(QFrame):
    """Horizontal Insights footer banner."""
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("InsightsCard")
        self.setFixedHeight(54)
        self.setStyleSheet(
            """
            QFrame#InsightsCard {
                background-color: rgba(20, 21, 38, 0.45);
                border-radius: 12px;
                border: 1px solid rgba(255, 255, 255, 0.03);
            }
        """
        )
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)
        
        colors = color_from_scheme(ColorScheme.DARK)
        self._icon_lbl = QLabel("\u2728")
        self._icon_lbl.setStyleSheet("font-size: 14px; background: transparent; border: none;")
        layout.addWidget(self._icon_lbl)
        
        self._text_lbl = QLabel("Your back volume is improving consistently. Keep focusing on progressive overload.")
        self._text_lbl.setStyleSheet(f"color: {colors.text_secondary}; font-size: 12px; font-weight: 500; background: transparent; border: none;")
        layout.addWidget(self._text_lbl, 1)
        
    def update_data(self, data: DashboardData) -> None:
        recs = getattr(data, "recommendations", [])
        if recs and len(recs) > 1:
            title = getattr(recs[1], "title", "")
            if title:
                self._text_lbl.setText(title)
        else:
            self._text_lbl.setText("Focus on progressive overload and maintain dynamic recovery cycles.")


class DashboardView(QWidget):
    """Main dashboard view — orchestrates widgets, signals, and data flow."""

    start_workout_clicked = Signal()
    view_all_prs_clicked = Signal()
    weekly_review_clicked = Signal()
    view_recommendations_clicked = Signal()
    log_weight_clicked = Signal()
    import_program_clicked = Signal()
    set_goal_clicked = Signal()

    def __init__(
        self,
        db: Any = None,
        prog_mgr: Any = None,
        nutrition_service: Any = None,
        controller: DashboardController | None = None,
        motion: MotionService | None = None,
    ) -> None:
        super().__init__()
        self._db = db
        self._prog_mgr = prog_mgr
        self._nutrition_service = nutrition_service
        self._motion = motion

        if controller:
            self._controller = controller
        else:
            self._build_default_controller(db, prog_mgr)

        self._last_data: DashboardData | None = None
        self._build_ui()
        self._connect_signals()

    def set_motion_service(self, motion: MotionService) -> None:
        self._motion = motion
        for w in self._widgets:
            if hasattr(w, "set_motion_service"):
                w.set_motion_service(motion)

    def _build_default_controller(self, db: Any, prog_mgr: Any) -> None:
        from modules.gymbrain.services.decision_engine import DecisionEngine
        from modules.workout.application.pr_engine import PREngine

        nutrition_provider = (
            getattr(self._nutrition_service, "provider", None)
            if self._nutrition_service
            else None
        )
        engine = (
            DecisionEngine.from_production(db=db, nutrition_provider=nutrition_provider)
            if db
            else None
        )
        pr_engine = PREngine(db) if db else None
        self._controller = DashboardController(
            db=db,
            decision_engine=engine,
            pr_engine=pr_engine,
            prog_mgr=prog_mgr,
            nutrition_service=self._nutrition_service,
        )

    def _build_ui(self) -> None:
        self.setStyleSheet("DashboardView { background: transparent; }")
        self._scroll = ScrollContainer()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._scroll)

        layout = self._scroll.content_layout
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        main = QVBoxLayout()
        main.setContentsMargins(24, 24, 24, 24)
        main.setSpacing(16)
        layout.insertLayout(0, main)

        # 1. Full-Width Hero Header
        self._hero = HeroWidget(motion=self._motion)
        main.addWidget(self._hero)

        # 2. Grid Container (2 Columns)
        grid_widget = QWidget()
        grid_widget.setStyleSheet("background: transparent;")
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(16)

        # Row 0, Column 0: Today's Mission (Existing)
        self._mission = MissionRecoveryWidget(prog_mgr=self._prog_mgr, db=self._db, motion=self._motion)
        grid_layout.addWidget(self._mission, 0, 0)

        # Row 0, Column 1: AI Coach (Existing)
        self._coach = CoachPredictionsWidget(motion=self._motion)
        grid_layout.addWidget(self._coach, 0, 1)

        # Row 1, Column 0: Weekly Progress (Existing)
        self._progress = ProgressWidget(motion=self._motion)
        grid_layout.addWidget(self._progress, 1, 0)

        # Row 1, Column 1: Recovery Overview (New compact card)
        self._recovery_card = RecoveryCard()
        grid_layout.addWidget(self._recovery_card, 1, 1)

        # Row 2: Nutrition Widget (Spans both columns)
        from ui.dashboard.dashboard_widgets.nutrition_widget import NutritionWidget
        self._nutrition_widget = NutritionWidget()
        grid_layout.addWidget(self._nutrition_widget, 2, 0, 1, 2)

        main.addWidget(grid_widget)

        # 3. Full-Width Insights Card at bottom
        self._insights_card = InsightsCard()
        main.addWidget(self._insights_card)

        self._widgets = [
            self._hero,
            self._mission,
            self._coach,
            self._progress,
            self._recovery_card,
            self._nutrition_widget,
            self._insights_card,
        ]

    def _connect_signals(self) -> None:
        # Forward widget signals to DashboardView signals
        self._hero.start_workout_clicked.connect(self.start_workout_clicked.emit)
        self._hero.weekly_review_clicked.connect(self.weekly_review_clicked.emit)

        self._mission.start_workout_clicked.connect(self.start_workout_clicked.emit)
        self._mission.import_program_clicked.connect(self.import_program_clicked.emit)

        # Controller → view update
        self._controller.data_updated.connect(self._on_data_updated)

    def _on_data_updated(self, data: DashboardData) -> None:
        self._last_data = data
        for w in self._widgets:
            w.update_data(data)

    def refresh(self) -> None:
        self._controller.refresh()

    def controller(self) -> DashboardController:
        return self._controller
