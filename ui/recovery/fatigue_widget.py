"""Fatigue Widget — shows fatigue level with color-coded indicator."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QProgressBar, QWidget

from ui.dashboard.dashboard_widgets.base_card import DashboardCard

FATIGUE_COLORS = {
    "low": "#4ADE80",
    "moderate": "#FBBF24",
    "high": "#EF4444",
    "very_high": "#A855F7",
}


class FatigueWidget(DashboardCard):
    """Shows fatigue level with score and detail breakdown."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="FATIGUE", parent=parent)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setTextVisible(False)
        self._progress.setFixedHeight(16)
        self._progress.setStyleSheet("""
            QProgressBar { background-color: #1E293B; border-radius: 8px; border: none; }
            QProgressBar::chunk { border-radius: 8px; }
        """)
        self.add_content(self._progress)

        self._value_label = QLabel("--/100")
        self._value_label.setStyleSheet("font-size: 24px; font-weight: 700; color: #F1F5F9;")
        self._value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_content(self._value_label)

        self._detail_label = QLabel("")
        self._detail_label.setStyleSheet("color: #94A3B8; font-size: 12px;")
        self._detail_label.setWordWrap(True)
        self._detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_content(self._detail_label)

    def update_data(self, data: Any) -> None:
        fatigue_score = getattr(data, "recovery_fatigue_score", 0.0) or 0.0

        color = FATIGUE_COLORS["low"]
        level = "low"
        if fatigue_score >= 70:
            color = FATIGUE_COLORS["very_high"]
            level = "very_high"
        elif fatigue_score >= 50:
            color = FATIGUE_COLORS["high"]
            level = "high"
        elif fatigue_score >= 30:
            color = FATIGUE_COLORS["moderate"]
            level = "moderate"

        self._progress.setValue(int(fatigue_score))
        self._progress.setStyleSheet(f"""
            QProgressBar {{ background-color: #1E293B; border-radius: 8px; border: none; }}
            QProgressBar::chunk {{ background-color: {color}; border-radius: 8px; }}
        """)
        self._value_label.setText(f"{fatigue_score:.0f}/100")
        self._detail_label.setText(f"Fatigue level: {level.upper().replace('_', ' ')}")
