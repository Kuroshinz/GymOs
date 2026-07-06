"""Readiness Widget — shows training readiness assessment."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QWidget

from ui.dashboard.dashboard_widgets.base_card import DashboardCard

READINESS_COLORS = {
    "ready": "#4ADE80",
    "good": "#FBBF24",
    "caution": "#FB923C",
    "fatigued": "#EF4444",
    "deload": "#A855F7",
}

READINESS_EMOJIS = {
    "ready": "🚀",
    "good": "✅",
    "caution": "⚠️",
    "fatigued": "😴",
    "deload": "🔄",
}


class ReadinessWidget(DashboardCard):
    """Shows training readiness level with color-coded indicator."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="TRAINING READINESS", parent=parent)

        self._emoji_label = QLabel("--")
        self._emoji_label.setStyleSheet("font-size: 40px;")
        self._emoji_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_content(self._emoji_label)

        self._level_label = QLabel("No Data")
        self._level_label.setStyleSheet("font-size: 18px; font-weight: 700; color: #F1F5F9;")
        self._level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_content(self._level_label)

        self._score_label = QLabel("")
        self._score_label.setStyleSheet("color: #94A3B8; font-size: 14px;")
        self._score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_content(self._score_label)

        self._action_label = QLabel("")
        self._action_label.setStyleSheet("color: #818CF8; font-size: 12px; padding: 8px 0px;")
        self._action_label.setWordWrap(True)
        self._action_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_content(self._action_label)

    def update_data(self, data: Any) -> None:
        level = getattr(data, "recovery_level", "") or ""
        score = getattr(data, "recovery_score", 0.0) or 0.0
        flags = getattr(data, "recovery_flags", []) or []

        level_key = level.lower() if level else "good"
        emoji = READINESS_EMOJIS.get(level_key, "✅")
        color = READINESS_COLORS.get(level_key, "#FBBF24")

        self._emoji_label.setText(emoji)
        display = level_key.upper().replace("_", " ")
        self._level_label.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {color};")
        self._level_label.setText(display)
        self._score_label.setText(f"Readiness Score: {score:.0f}/100")

        if flags:
            self._action_label.setText(f"⚠ {'; '.join(flags[:2])}")
        else:
            self._action_label.setText("Continue current training plan.")
