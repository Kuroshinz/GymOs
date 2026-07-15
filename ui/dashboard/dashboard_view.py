"""Dashboard View — premium overview matching the GymOS dashboard design.

External API is backward-compatible:
  - Constructor: DashboardView(db, prog_mgr, nutrition_service, controller, motion)
  - Methods: refresh(), controller(), set_motion_service(motion)
  - Signals: start_workout_clicked, view_all_prs_clicked, weekly_review_clicked,
             view_recommendations_clicked, log_weight_clicked, import_program_clicked,
             set_goal_clicked, view_recovery_clicked

Layout (top → bottom):
  1. Welcome header (greeting + date)
  2. Metric strip (Training Load, Calories, Active Time, Score, Recovery)
  3. Weekly Progress | Muscle Group Focus | Recent Workouts
  4. Recovery Status | Nutrition Overview | AI Coach Recommendation
  5. Achievements | Streak | Next Milestone | Body Weight
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from ui.dashboard.dashboard_controller import DashboardController
from ui.dashboard.dashboard_models import DashboardData
from ui.dashboard.dashboard_widgets.ai_coach_widget import AICoachWidget
from ui.dashboard.dashboard_widgets.card_kit import make_label
from ui.dashboard.dashboard_widgets.highlights_widget import HighlightsWidget
from ui.dashboard.dashboard_widgets.muscle_focus_widget import MuscleFocusWidget
from ui.dashboard.dashboard_widgets.nutrition_overview_widget import NutritionOverviewWidget
from ui.dashboard.dashboard_widgets.recent_workouts_widget import RecentWorkoutsWidget
from ui.dashboard.dashboard_widgets.recovery_status_widget import RecoveryStatusWidget
from ui.dashboard.dashboard_widgets.stat_strip_widget import StatStripWidget
from ui.dashboard.dashboard_widgets.weekly_progress_widget import WeeklyProgressWidget
from ui.design_system.layout import ScrollContainer
from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.experience.motion_service import MotionService

C = color_from_scheme(ColorScheme.DARK)


class _DashboardSection(Protocol):
    def update_data(self, data: DashboardData) -> None: ...
    def set_motion_service(self, motion: MotionService) -> None: ...


class DashboardView(QWidget):
    """Main dashboard view — premium overview surface."""

    start_workout_clicked = Signal()
    view_all_prs_clicked = Signal()
    weekly_review_clicked = Signal()
    view_recommendations_clicked = Signal()
    log_weight_clicked = Signal()
    import_program_clicked = Signal()
    set_goal_clicked = Signal()
    view_recovery_clicked = Signal()

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
        main.setContentsMargins(4, 4, 28, 40)
        main.setSpacing(20)
        layout.insertLayout(0, main)

        main.addLayout(self._build_header())

        # 1. Metric strip
        self._stats = StatStripWidget(motion=self._motion)
        main.addWidget(self._stats)

        # 2. Weekly Progress | Muscle Focus | Recent Workouts
        self._weekly = WeeklyProgressWidget(motion=self._motion)
        self._muscle = MuscleFocusWidget(motion=self._motion)
        self._recent = RecentWorkoutsWidget(motion=self._motion)
        row1 = QHBoxLayout()
        row1.setContentsMargins(0, 0, 0, 0)
        row1.setSpacing(16)
        row1.addWidget(self._weekly, 5)
        row1.addWidget(self._muscle, 3)
        row1.addWidget(self._recent, 3)
        main.addLayout(row1)

        # 3. Recovery | Nutrition | AI Coach
        self._recovery = RecoveryStatusWidget(motion=self._motion)
        self._nutrition = NutritionOverviewWidget(motion=self._motion)
        self._coach = AICoachWidget(motion=self._motion)
        row2 = QHBoxLayout()
        row2.setContentsMargins(0, 0, 0, 0)
        row2.setSpacing(16)
        row2.addWidget(self._recovery, 1)
        row2.addWidget(self._nutrition, 1)
        row2.addWidget(self._coach, 1)
        main.addLayout(row2)

        # 4. Highlights row
        self._highlights = HighlightsWidget(motion=self._motion)
        main.addWidget(self._highlights)

        main.addStretch()

        self._widgets: list[_DashboardSection] = [
            self._stats, self._weekly, self._muscle, self._recent,
            self._recovery, self._nutrition, self._coach, self._highlights,
        ]

    def _build_header(self) -> QHBoxLayout:
        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 4)
        header.setSpacing(4)

        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        self._welcome = make_label("Welcome back!", size=22, weight=800, color=C.text_primary, letter_spacing="-0.02em")
        text_col.addWidget(self._welcome)
        text_col.addWidget(make_label("Here's your overview for today.", size=13, weight=400, color=C.text_secondary))
        header.addLayout(text_col)
        header.addStretch()

        date_pill = make_label(datetime.now().strftime("%A, %b %d, %Y"), size=13, weight=600, color=C.text_secondary)
        date_pill.setStyleSheet(
            f"color: {C.text_secondary}; font-size: 13px; font-weight: 600; "
            f"background: {C.surface}; border: 1px solid {C.border}; "
            f"border-radius: 12px; padding: 9px 16px;"
        )
        header.addWidget(date_pill)
        return header

    def _connect_signals(self) -> None:
        self._recent.action_clicked.connect(self.view_all_prs_clicked.emit)
        self._recovery.view_details_clicked.connect(self.view_recovery_clicked.emit)
        self._nutrition.view_details_clicked.connect(self.view_recommendations_clicked.emit)
        self._coach.chat_clicked.connect(self.view_recommendations_clicked.emit)

        self._controller.data_updated.connect(self._on_data_updated)

    def _on_data_updated(self, data: DashboardData) -> None:
        self._last_data = data
        name = (data.user_name or "").strip()
        self._welcome.setText(f"Welcome back, {name}!" if name else "Welcome back!")
        for w in self._widgets:
            w.update_data(data)

    def refresh(self) -> None:
        self._controller.refresh()

    def controller(self) -> DashboardController:
        return self._controller
