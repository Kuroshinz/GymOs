"""Weekly volume card — top muscles with effective sets, frequency, and trend."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .base_card import DashboardCard


class VolumeWidget(DashboardCard):
    """Shows weekly volume for priority muscles.

    For each muscle:
      - Name
      - Effective sets count
      - Target range (MEV-MAV)
      - Frequency (x/week)
      - Trend arrow (↑ ↓ →)
    """

    HEADER_STYLE = "color: #64748B; font-size: 10px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;"

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="WEEKLY VOLUME", parent=parent)
        self._container = QVBoxLayout()
        self._container.setContentsMargins(0, 0, 0, 0)
        self._container.setSpacing(6)
        self.add_layout(self._container)

    def update(self, data: Any) -> None:
        """Update with dashboard data."""
        while self._container.count():
            item = self._container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        muscles = getattr(data, "priority_muscles", []) or []

        if not muscles:
            msg = QLabel(
                "No volume data yet. Complete a workout to see weekly volume."
            )
            msg.setStyleSheet(
                "color: #64748B; font-size: 13px; padding: 20px 0px;"
            )
            msg.setWordWrap(True)
            msg.setAlignment(Qt.AlignCenter)
            self._container.addWidget(msg)
            return

        # Header row
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 4)
        header_layout.setSpacing(6)

        headers = ["Muscle", "Sets", "Target", "Freq", ""]
        widths = [100, 36, 44, 40, 20]
        for h, w in zip(headers, widths, strict=True):
            lbl = QLabel(h)
            lbl.setStyleSheet(self.HEADER_STYLE)
            lbl.setFixedWidth(w)
            header_layout.addWidget(lbl)
        header_layout.addStretch()
        self._container.addWidget(header)

        for muscle in muscles[:6]:
            row = self._build_volume_row(muscle)
            self._container.addWidget(row)

    def _build_volume_row(self, muscle: Any) -> QWidget:
        # Extract fields
        if hasattr(muscle, "display_name"):
            name = muscle.display_name or "Unknown"
            effective_sets = getattr(muscle, "current_sets", 0) or 0
            target_min = getattr(muscle, "recommended_min_sets", 0) or 0
            target_max = getattr(muscle, "recommended_max_sets", 0) or 0
            freq = getattr(muscle, "weekly_frequency", 0) or 0
            progress = getattr(muscle, "progress", "") or "Stable"
            status_val = getattr(muscle, "status", "optimal")
            if hasattr(status_val, "value"):
                status_val = status_val.value
        else:
            muscle_data = muscle if isinstance(muscle, dict) else {}
            name = muscle_data.get("display_name", str(muscle))
            effective_sets = muscle_data.get("current_sets", 0) or 0
            target_min = muscle_data.get("recommended_min_sets", 0) or 0
            target_max = muscle_data.get("recommended_max_sets", 0) or 0
            freq = muscle_data.get("weekly_frequency", 0) or 0
            progress = muscle_data.get("progress", "") or "Stable"
            status_val = muscle_data.get("status", "optimal") or "optimal"

        # Trend
        trend_map = {
            "Improving": ("↑", "#4ADE80"),
            "Slightly improving": ("↗", "#A3E635"),
            "Stable": ("→", "#94A3B8"),
            "Slightly declining": ("↘", "#FBBF24"),
            "Declining": ("↓", "#F87171"),
            "Maintaining": ("→", "#94A3B8"),
        }
        trend_char, trend_color = trend_map.get(progress, ("→", "#94A3B8"))

        # Status color for sets
        status_str = str(status_val).lower() if status_val else "optimal"
        if status_str in ("low", "high"):
            sets_color = "#F87171"
        elif status_str in ("building",):
            sets_color = "#FBBF24"
        elif status_str in ("optimal",):
            sets_color = "#4ADE80"
        else:
            sets_color = "#818CF8"

        row = QFrame()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 2, 0, 2)
        row_layout.setSpacing(6)

        # Name
        name_label = QLabel(name)
        name_label.setStyleSheet("color: #F1F5F9; font-size: 13px; font-weight: 600;")
        name_label.setFixedWidth(100)
        row_layout.addWidget(name_label)

        # Sets
        sets_label = QLabel(f"{effective_sets:.0f}")
        sets_label.setStyleSheet(f"color: {sets_color}; font-size: 13px; font-weight: 700;")
        sets_label.setFixedWidth(36)
        row_layout.addWidget(sets_label)

        # Target range
        target_label = QLabel(f"{target_min:.0f}-{target_max:.0f}")
        target_label.setStyleSheet("color: #64748B; font-size: 11px;")
        target_label.setFixedWidth(44)
        row_layout.addWidget(target_label)

        # Frequency
        freq_label = QLabel(f"{freq}x/wk")
        freq_label.setStyleSheet("color: #64748B; font-size: 11px;")
        freq_label.setFixedWidth(40)
        row_layout.addWidget(freq_label)

        # Trend
        trend_label = QLabel(trend_char)
        trend_label.setStyleSheet(f"color: {trend_color}; font-size: 16px; font-weight: 700;")
        trend_label.setFixedWidth(20)
        row_layout.addWidget(trend_label)

        row_layout.addStretch()
        return row
