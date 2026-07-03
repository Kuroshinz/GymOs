"""Quick actions card — one-click buttons for common tasks."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QGridLayout, QPushButton

from .base_card import DashboardCard


class QuickActionsWidget(DashboardCard):
    """Grid of action buttons for common dashboard tasks.

    Current actions:
      - Start Workout
      - Log Body Weight
      - Import Workout Program
      - View Weekly Review
      - Open Recommendations

    Future: Log Meal, Sleep, Recovery (when modules are implemented)
    """

    start_workout_clicked = Signal()
    log_weight_clicked = Signal()
    import_program_clicked = Signal()
    weekly_review_clicked = Signal()
    view_recommendations_clicked = Signal()

    BUTTON_BASE = """
        QPushButton {
            background-color: #334155;
            color: #F1F5F9;
            border: none;
            border-radius: 8px;
            height: 44px;
            font-size: 13px;
            font-weight: 600;
            padding: 0 16px;
        }
        QPushButton:hover {
            background-color: #475569;
        }
    """

    BUTTON_PRIMARY = """
        QPushButton {
            background-color: #818CF8;
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            height: 44px;
            font-size: 13px;
            font-weight: 600;
            padding: 0 16px;
        }
        QPushButton:hover {
            background-color: #6366F1;
        }
    """

    def __init__(self, parent: QFrame | None = None) -> None:
        super().__init__(title="QUICK ACTIONS", parent=parent)

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(10)

        self._start_btn = QPushButton("▶  Start Workout")
        self._start_btn.setStyleSheet(self.BUTTON_PRIMARY)
        self._start_btn.clicked.connect(self.start_workout_clicked.emit)

        self._weight_btn = QPushButton("⚖️  Log Body Weight")
        self._weight_btn.setStyleSheet(self.BUTTON_BASE)
        self._weight_btn.clicked.connect(self.log_weight_clicked.emit)

        self._import_btn = QPushButton("📥  Import Program")
        self._import_btn.setStyleSheet(self.BUTTON_BASE)
        self._import_btn.clicked.connect(self.import_program_clicked.emit)

        self._review_btn = QPushButton("📊  Weekly Review")
        self._review_btn.setStyleSheet(self.BUTTON_BASE)
        self._review_btn.clicked.connect(self.weekly_review_clicked.emit)

        self._recs_btn = QPushButton("📋  Recommendations")
        self._recs_btn.setStyleSheet(self.BUTTON_BASE)
        self._recs_btn.clicked.connect(self.view_recommendations_clicked.emit)

        grid.addWidget(self._start_btn, 0, 0)
        grid.addWidget(self._weight_btn, 0, 1)
        grid.addWidget(self._import_btn, 1, 0)
        grid.addWidget(self._review_btn, 1, 1)
        grid.addWidget(self._recs_btn, 2, 0, 1, 2)

        self.add_layout(grid)

    def update(self, data: Any) -> None:
        """No-op — buttons are static. Signal connections handle actions."""
        pass
