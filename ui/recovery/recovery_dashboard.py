"""Recovery Dashboard — main container widget for the Recovery Intelligence view.

Composed of individual widgets showing recovery score, readiness, trend,
sleep/stress, fatigue, deload status, timeline, and weekly averages.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from PySide6.QtWidgets import QGridLayout, QWidget

from ui.dashboard.dashboard_widgets.base_card import DashboardCard
from ui.recovery.deload_widget import DeloadWidget
from ui.recovery.fatigue_widget import FatigueWidget
from ui.recovery.readiness_widget import ReadinessWidget
from ui.recovery.recovery_score_widget import RecoveryScoreWidget
from ui.recovery.recovery_trend_widget import RecoveryTrendWidget
from ui.recovery.sleep_stress_widget import SleepStressWidget
from ui.recovery.timeline_widget import RecoveryTimelineWidget
from ui.recovery.weekly_widget import WeeklyRecoveryWidget


@dataclass
class RecoveryDashboardData:
    """Adapter data object consumed by all Recovery Dashboard widgets.
    Bridges RecoverySnapshot + service data to the widget interface.
    """
    recovery_score: float = 0.0
    recovery_level: str = ""
    recovery_flags: list = field(default_factory=list)
    recovery_sleep_score: float = 0.0
    recovery_sleep_hours: float = 0.0
    recovery_stress_score: float = 0.0
    recovery_fatigue_score: float = 0.0
    recovery_trend: Any = None
    recovery_active_deload: Any = None
    recovery_scores: list = field(default_factory=list)
    recovery_scores_count: int = 0
    recovery_weekly: list = field(default_factory=list)
    recovery_action: str = ""


class RecoveryDashboard(DashboardCard):
    """Main Recovery Dashboard container.

    Usage:
        dashboard = RecoveryDashboard()
        dashboard.refresh(service.get_snapshot())
    """

    def __init__(self, title: str = "Recovery Dashboard", parent: QWidget | None = None) -> None:
        super().__init__(title=title, parent=parent)

        self._top_row = QGridLayout()
        self._top_row.setContentsMargins(0, 0, 0, 8)
        self._top_row.setSpacing(8)

        self._score_widget = RecoveryScoreWidget()
        self._top_row.addWidget(self._score_widget, 0, 0)

        self._readiness_widget = ReadinessWidget()
        self._top_row.addWidget(self._readiness_widget, 0, 1)

        self._trend_widget = RecoveryTrendWidget()
        self._top_row.addWidget(self._trend_widget, 0, 2)

        top_container = QWidget()
        top_container.setLayout(self._top_row)
        self.add_content(top_container)

        # Middle row: Sleep/Stress + Fatigue + Deload
        self._middle_row = QGridLayout()
        self._middle_row.setContentsMargins(0, 0, 0, 8)
        self._middle_row.setSpacing(8)

        self._sleep_stress_widget = SleepStressWidget()
        self._middle_row.addWidget(self._sleep_stress_widget, 0, 0)

        self._fatigue_widget = FatigueWidget()
        self._middle_row.addWidget(self._fatigue_widget, 0, 1)

        self._deload_widget = DeloadWidget()
        self._middle_row.addWidget(self._deload_widget, 0, 2)

        mid_container = QWidget()
        mid_container.setLayout(self._middle_row)
        self.add_content(mid_container)

        # Bottom row: Timeline + Weekly
        self._bottom_row = QGridLayout()
        self._bottom_row.setContentsMargins(0, 0, 0, 0)
        self._bottom_row.setSpacing(8)

        self._timeline_widget = RecoveryTimelineWidget()
        self._bottom_row.addWidget(self._timeline_widget, 0, 0)

        self._weekly_widget = WeeklyRecoveryWidget()
        self._bottom_row.addWidget(self._weekly_widget, 0, 1)

        bottom_container = QWidget()
        bottom_container.setLayout(self._bottom_row)
        self.add_content(bottom_container)

    def refresh(self, data: Any) -> None:
        """Update all child widgets with recovery data from a RecoverySnapshot or service."""
        self._score_widget.update_data(data)
        self._readiness_widget.update_data(data)
        self._trend_widget.update_data(data)
        self._sleep_stress_widget.update_data(data)
        self._fatigue_widget.update_data(data)
        self._deload_widget.update_data(data)
        self._timeline_widget.update_data(data)
        self._weekly_widget.update_data(data)
