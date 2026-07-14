"""Recovery Trend Widget — shows recovery trend direction and weekly averages."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from ui.dashboard.dashboard_widgets.base_card import DashboardCard

TREND_COLORS = {
    "improving": "#4ADE80",
    "stable": "#FBBF24",
    "declining": "#EF4444",
    "volatile": "#A855F7",
}

TREND_ICONS = {
    "improving": "▲",
    "stable": "◆",
    "declining": "▼",
    "volatile": "◈",
}


class RecoveryTrendWidget(DashboardCard):
    """Shows recovery trend with icon, direction, slope, and weekly averages."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="RECOVERY TREND", parent=parent)

        self._icon_label = QLabel("◆")
        self._icon_label.setStyleSheet("font-size: 32px; color: #FBBF24;")
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_content(self._icon_label)

        self._direction_label = QLabel("No Data")
        self._direction_label.setStyleSheet("font-size: 16px; font-weight: 700; color: #F1F5F9;")
        self._direction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_content(self._direction_label)

        self._details_label = QLabel("")
        self._details_label.setStyleSheet("color: #94A3B8; font-size: 12px;")
        self._details_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._details_label.setWordWrap(True)
        self.add_content(self._details_label)

        # Weekly averages row
        self._weekly_row = QWidget()
        self._weekly_layout = QHBoxLayout(self._weekly_row)
        self._weekly_layout.setContentsMargins(0, 4, 0, 0)
        self._weekly_layout.setSpacing(8)
        self._week_labels: list[QLabel] = []
        for _ in range(4):
            lbl = QLabel("--")
            lbl.setStyleSheet("color: #64748B; font-size: 11px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._weekly_layout.addWidget(lbl)
            self._week_labels.append(lbl)
        self.add_content(self._weekly_row)

    def update_data(self, data: Any) -> None:
        trend_data = getattr(data, "recovery_trend", None) or {}
        if isinstance(trend_data, dict):
            direction = trend_data.get("direction", "stable")
            slope = trend_data.get("slope", 0.0)
            weekly = trend_data.get("weekly_averages", [])
        else:
            direction = getattr(trend_data, "direction", "stable")
            if hasattr(direction, "value"):
                direction = direction.value
            slope = getattr(trend_data, "slope", 0.0)
            weekly = getattr(trend_data, "weekly_averages", [])

        dir_key = str(direction).lower()
        color = TREND_COLORS.get(dir_key, "#FBBF24")
        icon = TREND_ICONS.get(dir_key, "◆")

        self._icon_label.setStyleSheet(f"font-size: 32px; color: {color};")
        self._icon_label.setText(icon)
        self._direction_label.setText(dir_key.upper().replace("_", " "))
        if isinstance(slope, (int, float)):
            self._details_label.setText(f"Slope: {slope:+.2f}/day")
        else:
            self._details_label.setText("")

        for i, lbl in enumerate(self._week_labels):
            if i < len(weekly):
                val = weekly[i]
                avg = val.get("average", 0) if isinstance(val, dict) else val
                lbl.setText(f"W{i+1}: {avg:.0f}")
                lbl.setStyleSheet("color: #94A3B8; font-size: 11px;")
            else:
                lbl.setText("--")
                lbl.setStyleSheet("color: #64748B; font-size: 11px;")
