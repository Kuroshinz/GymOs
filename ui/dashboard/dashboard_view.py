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

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from ui.dashboard.dashboard_controller import DashboardController
from ui.dashboard.dashboard_models import DashboardData
from ui.dashboard.dashboard_widgets.actions_widget import ActionsWidget
from ui.dashboard.dashboard_widgets.coach_widget import CoachPredictionsWidget
from ui.dashboard.dashboard_widgets.hero_widget import HeroWidget
from ui.dashboard.dashboard_widgets.mission_widget import MissionRecoveryWidget
from ui.dashboard.dashboard_widgets.progress_widget import ProgressWidget
from ui.design_system.components.section_header import SectionHeader
from ui.design_system.layout import ScrollContainer
from ui.experience.motion_service import MotionService

S = 0  # SpacingTokens accessed via _px helpers in widgets


class DashboardView(QWidget):
    """Main dashboard view — orchestrates widgets, signals, and data flow.

    Signals (backward-compatible):
    """

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
        main.setContentsMargins(0, 16, 40, 64)
        main.setSpacing(0)
        layout.insertLayout(0, main)

        # 1. Hero
        self._hero = HeroWidget(motion=self._motion)
        main.addWidget(self._hero)

        main.addSpacing(48)

        # 2. Today's Mission
        self._build_section_header(main, "Today's Mission", "Your next training session")
        main.addSpacing(20)
        self._mission = MissionRecoveryWidget(motion=self._motion)
        main.addWidget(self._mission)

        main.addSpacing(48)

        # 3. Coach
        self._build_section_header(main, "Coach", "Personalized guidance")
        main.addSpacing(20)
        self._coach = CoachPredictionsWidget(motion=self._motion)
        main.addWidget(self._coach)

        main.addSpacing(48)

        # 4. Progress
        self._build_section_header(main, "Progress", "Your training journey")
        main.addSpacing(20)
        self._progress = ProgressWidget(motion=self._motion)
        main.addWidget(self._progress)

        main.addSpacing(48)

        # 5. Records & Actions
        self._build_section_header(main, "Records & Actions", "Achievements & quick tasks")
        main.addSpacing(20)
        self._actions = ActionsWidget(motion=self._motion)
        main.addWidget(self._actions)

        main.addStretch()

        self._widgets = [self._hero, self._mission, self._coach, self._progress, self._actions]

    @staticmethod
    def _build_section_header(parent: QVBoxLayout, title: str, subtitle: str) -> None:
        header = SectionHeader(title=title, subtitle=subtitle)
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(header)
        parent.addLayout(hbox)

    def _connect_signals(self) -> None:
        # Forward widget signals to DashboardView signals
        self._hero.start_workout_clicked.connect(self.start_workout_clicked.emit)
        self._hero.weekly_review_clicked.connect(self.weekly_review_clicked.emit)

        self._mission.start_workout_clicked.connect(self.start_workout_clicked.emit)
        self._mission.import_program_clicked.connect(self.import_program_clicked.emit)

        self._actions.start_workout_clicked.connect(self.start_workout_clicked.emit)
        self._actions.log_weight_clicked.connect(self.log_weight_clicked.emit)
        self._actions.set_goal_clicked.connect(self.set_goal_clicked.emit)
        self._actions.import_program_clicked.connect(self.import_program_clicked.emit)
        self._actions.view_all_prs_clicked.connect(self.view_all_prs_clicked.emit)
        self._actions.weekly_review_clicked.connect(self.weekly_review_clicked.emit)

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
