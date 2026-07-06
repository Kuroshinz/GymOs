"""Recovery Score Widget — shows the current composite recovery score (0-100)."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QProgressBar, QWidget

from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class RecoveryScoreWidget(DashboardCard):
    """Shows the current recovery score with color-coded progress bar."""

    SCORE_COLORS = {
        "high": "#4ADE80",
        "good": "#FBBF24",
        "caution": "#FB923C",
        "low": "#EF4444",
    }

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="RECOVERY SCORE", parent=parent)

        self._score_label = QLabel("--/100")
        self._score_label.setStyleSheet("font-size: 36px; font-weight: 700; color: #F1F5F9;")
        self._score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_content(self._score_label)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        self._progress.setValue(0)
        self._progress.setTextVisible(False)
        self._progress.setFixedHeight(12)
        self._progress.setStyleSheet("""
            QProgressBar {
                background-color: #1E293B;
                border-radius: 6px;
                border: none;
            }
            QProgressBar::chunk {
                border-radius: 6px;
            }
        """)
        self.add_content(self._progress)

        self._level_label = QLabel("No Data")
        self._level_label.setStyleSheet("color: #94A3B8; font-size: 14px;")
        self._level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_content(self._level_label)

    def update_score(self, score: float, level: str = "", explanation: str = "") -> None:
        self._score_label.setText(f"{score:.0f}/100")

        color = self.SCORE_COLORS["good"]
        if score >= 80:
            color = self.SCORE_COLORS["high"]
        elif score >= 60:
            color = self.SCORE_COLORS["good"]
        elif score >= 40:
            color = self.SCORE_COLORS["caution"]
        else:
            color = self.SCORE_COLORS["low"]

        self._progress.setValue(int(score))
        self._progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: #1E293B;
                border-radius: 6px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 6px;
            }}
        """)

        display = level.upper().replace("_", " ") if level else "No Data"
        self._level_label.setText(display)

    def update_data(self, data: Any) -> None:
        score = getattr(data, "recovery_score", 0.0) or 0.0
        level = getattr(data, "recovery_level", "") or ""
        self.update_score(score, level)
