"""Dashboard view — scrollable card-based training intelligence hub.

Layout order (per spec):
  Header → Goal Progress → Recommendation → Today's Workout →
  Priority Muscles → Recovery Status → Weekly Volume →
  Recent PRs → Nutrition Summary → Quick Actions
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QScrollArea, QVBoxLayout, QWidget

from ui.dashboard.dashboard_controller import DashboardController
from ui.dashboard.dashboard_models import DashboardData
from ui.dashboard.dashboard_widgets.goal_progress_widget import GoalProgressWidget
from ui.dashboard.dashboard_widgets.header_widget import DashboardHeader
from ui.dashboard.dashboard_widgets.nutrition_widget import NutritionWidget
from ui.dashboard.dashboard_widgets.priority_muscles_widget import PriorityMusclesWidget
from ui.dashboard.dashboard_widgets.pr_widget import PRWidget
from ui.dashboard.dashboard_widgets.quick_actions_widget import QuickActionsWidget
from ui.dashboard.dashboard_widgets.recommendation_widget import RecommendationWidget
from ui.dashboard.dashboard_widgets.recovery_widget import RecoveryWidget
from ui.dashboard.dashboard_widgets.volume_widget import VolumeWidget
from ui.dashboard.dashboard_widgets.workout_widget import WorkoutWidget


class DashboardView(QWidget):
    """Main dashboard view — scrollable card layout.

    Assembles all dashboard widgets vertically in priority order.
    Connected to a DashboardController for data flow.
    """

    start_workout_clicked = Signal()
    view_all_prs_clicked = Signal()
    weekly_review_clicked = Signal()
    view_recommendations_clicked = Signal()
    log_weight_clicked = Signal()
    import_program_clicked = Signal()

    def __init__(
        self,
        db: Any = None,
        prog_mgr: Any = None,
        controller: DashboardController | None = None,
    ) -> None:
        super().__init__()
        self._db = db
        self._prog_mgr = prog_mgr

        if controller:
            self._controller = controller
        else:
            self._build_default_controller(db, prog_mgr)

        self._build_ui()
        self._connect_signals()

    def _build_default_controller(self, db: Any, prog_mgr: Any) -> None:
        """Auto-wire a controller with default engines."""
        from modules.gymbrain.services.decision_engine import DecisionEngine
        from modules.workout.application.pr_engine import PREngine

        engine = DecisionEngine.from_production(db=db) if db else None
        pr_engine = PREngine(db) if db else None

        self._controller = DashboardController(
            db=db,
            decision_engine=engine,
            pr_engine=pr_engine,
            prog_mgr=prog_mgr,
        )

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #0F172A;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #0F172A;
                width: 8px;
                border: none;
            }
            QScrollBar::handle:vertical {
                background-color: #334155;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #475569;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: #0F172A;")
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(32, 24, 32, 32)
        content_layout.setSpacing(16)

        # 1. Header
        self._header = DashboardHeader()
        content_layout.addWidget(self._header)

        # 2. Goal Progress
        self._goal_progress = GoalProgressWidget()
        content_layout.addWidget(self._goal_progress)

        # 3. Today's Recommendation
        self._recommendation = RecommendationWidget()
        content_layout.addWidget(self._recommendation)

        # 4. Today's Workout
        self._workout = WorkoutWidget()
        self._workout.start_workout_clicked.connect(self.start_workout_clicked.emit)
        content_layout.addWidget(self._workout)

        # 5. Priority Muscles
        self._priority_muscles = PriorityMusclesWidget()
        content_layout.addWidget(self._priority_muscles)

        # 6. Recovery Status
        self._recovery = RecoveryWidget()
        content_layout.addWidget(self._recovery)

        # 7. Weekly Volume
        self._volume = VolumeWidget()
        content_layout.addWidget(self._volume)

        # 8. Recent PRs
        self._prs = PRWidget()
        self._prs.view_all_prs_clicked.connect(self.view_all_prs_clicked.emit)
        content_layout.addWidget(self._prs)

        # 9. Nutrition Summary
        self._nutrition = NutritionWidget()
        content_layout.addWidget(self._nutrition)

        # 10. Quick Actions
        self._quick_actions = QuickActionsWidget()
        self._quick_actions.start_workout_clicked.connect(
            self.start_workout_clicked.emit
        )
        self._quick_actions.log_weight_clicked.connect(
            self.log_weight_clicked.emit
        )
        self._quick_actions.weekly_review_clicked.connect(
            self.weekly_review_clicked.emit
        )
        self._quick_actions.view_recommendations_clicked.connect(
            self.view_recommendations_clicked.emit
        )
        self._quick_actions.import_program_clicked.connect(
            self.import_program_clicked.emit
        )
        content_layout.addWidget(self._quick_actions)

        content_layout.addStretch()

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

    def _connect_signals(self) -> None:
        self._controller.data_updated.connect(self._on_data_updated)

    def _on_data_updated(self, data: DashboardData) -> None:
        """Update all widgets with fresh data."""
        self._header.update(data)
        self._goal_progress.update(data)
        self._recommendation.set_data(data)
        self._workout.update(data)
        self._priority_muscles.update(data)
        self._recovery.update(data)
        self._volume.update(data)
        self._prs.set_data(data)
        self._nutrition.update(data)
        self._quick_actions.update(data)

    def refresh(self) -> None:
        """Full dashboard refresh."""
        self._controller.refresh()

    def controller(self) -> DashboardController:
        return self._controller
