"""Dashboard header — user greeting, program info, key metrics."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout


class DashboardHeader(QFrame):
    """Top section of the dashboard with user greeting and key stats.

    Displays:
      - Time-based greeting
      - Current program name
      - Weight / Goal
      - Current streak
      - Total workouts
      - Weekly volume
      - Mesocycle week
    """

    STYLE = """
        DashboardHeader {
            background-color: #1E293B;
            border-radius: 16px;
            border: 1px solid #334155;
        }
    """
    GREETING_STYLE = "color: #F1F5F9; font-size: 28px; font-weight: 700;"
    PROGRAM_STYLE = "color: #818CF8; font-size: 16px; font-weight: 600;"
    STAT_VALUE_STYLE = "color: #F1F5F9; font-size: 20px; font-weight: 700;"
    STAT_LABEL_STYLE = "color: #64748B; font-size: 12px; font-weight: 500;"

    def __init__(self, parent: QFrame | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(self.STYLE)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(28, 24, 28, 24)
        self._layout.setSpacing(16)

        # Greeting
        self._greeting_label = QLabel()
        self._greeting_label.setStyleSheet(self.GREETING_STYLE)
        self._layout.addWidget(self._greeting_label)

        # Program name
        self._program_label = QLabel()
        self._program_label.setStyleSheet(self.PROGRAM_STYLE)
        self._layout.addWidget(self._program_label)

        # Stats row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(24)

        self._weight_label = self._make_stat()
        self._streak_label = self._make_stat()
        self._workouts_label = self._make_stat()
        self._volume_label = self._make_stat()
        self._week_label = self._make_stat()
        self._split_label = self._make_stat()

        stats_row.addWidget(self._weight_label)
        stats_row.addWidget(self._streak_label)
        stats_row.addWidget(self._workouts_label)
        stats_row.addWidget(self._volume_label)
        stats_row.addWidget(self._week_label)
        stats_row.addWidget(self._split_label)
        stats_row.addStretch()

        self._layout.addLayout(stats_row)

    def _make_stat(self) -> QFrame:
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        value = QLabel("--")
        value.setStyleSheet(self.STAT_VALUE_STYLE)
        layout.addWidget(value)

        label = QLabel("--")
        label.setStyleSheet(self.STAT_LABEL_STYLE)
        layout.addWidget(label)

        return frame

    def _set_stat(self, frame: QFrame, value: str, label: str) -> None:
        labels = frame.findChildren(QLabel)
        if len(labels) >= 2:
            labels[0].setText(value)
            labels[1].setText(label)

    def _greeting(self) -> str:
        hour = datetime.now().hour
        if hour < 12:
            return "Good Morning"
        elif hour < 18:
            return "Good Afternoon"
        return "Good Evening"

    def update(self, data: Any) -> None:
        """Update header with dashboard data."""
        name = getattr(data, "user_name", "") or ""
        greeting = self._greeting()
        if name:
            self._greeting_label.setText(f"{greeting}, {name}")
        else:
            self._greeting_label.setText(greeting)

        prog = getattr(data, "current_program", "") or "No active program"
        self._program_label.setText(prog)

        # Weight / Goal
        current_w = getattr(data, "current_weight", 0.0) or 0.0
        goal_w = getattr(data, "goal_weight_kg", 0.0) or getattr(data, "goal_weight", 0.0) or 0.0
        goal_str = f"{current_w:.1f} kg"
        if goal_w:
            goal_str += f" / {goal_w:.1f} kg"
        self._set_stat(self._weight_label, goal_str, "Weight / Goal")

        # Streak
        streak = getattr(data, "current_streak", 0) or 0
        self._set_stat(self._streak_label, f"{streak} days", "Current Streak")

        # Total workouts
        total = getattr(data, "total_workouts", 0) or 0
        self._set_stat(self._workouts_label, str(total), "Total Workouts")

        # Weekly volume
        vol = getattr(data, "weekly_volume_kg", 0.0) or 0.0
        self._set_stat(self._volume_label, f"{vol:.0f} kg", "Weekly Volume")

        # Mesocycle week
        week = getattr(data, "mesocycle_week", 0) or 0
        self._set_stat(self._week_label, f"Week {week}", "Mesocycle")

        # Current split day
        split_day = getattr(data, "current_split_day", "") or ""
        if not split_day and prog:
            split_day = prog
        self._set_stat(self._split_label, split_day if len(split_day) <= 20 else split_day[:17] + "...", "Split Day")
