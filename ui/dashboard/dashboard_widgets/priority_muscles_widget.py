"""Priority muscles card — shows each muscle's current volume vs target, recovery, and recommendation."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from .base_card import DashboardCard

STATUS_COLORS = {
    "low": "#F87171",
    "building": "#FBBF24",
    "optimal": "#4ADE80",
    "maintenance": "#818CF8",
    "high": "#F87171",
}

STATUS_LABELS = {
    "low": "Below MEV",
    "building": "Building",
    "optimal": "Optimal",
    "maintenance": "Maintenance",
    "high": "Above MRV",
}

TREND_ICONS = {
    "Improving": "↑",
    "Slightly improving": "↗",
    "Stable": "→",
    "Slightly declining": "↘",
    "Declining": "↓",
    "Maintaining": "→",
}

TREND_COLORS = {
    "Improving": "#4ADE80",
    "Slightly improving": "#A3E635",
    "Stable": "#94A3B8",
    "Slightly declining": "#FBBF24",
    "Declining": "#F87171",
    "Maintaining": "#94A3B8",
}


class PriorityMusclesWidget(DashboardCard):
    """Shows each priority muscle's training status at a glance.

    For each muscle:
      - Name with status dot
      - Current effective sets / Target range (MEV-MAV)
      - Recovery status
      - Trend arrow
      - Recommendation
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="PRIORITY MUSCLES", parent=parent)

        self._empty_label = QLabel(
            "No priority muscles defined. Set your training priorities "
            "in the program settings."
        )
        self._empty_label.setStyleSheet(
            "color: #64748B; font-size: 13px; padding: 16px 0px;"
        )
        self._empty_label.setWordWrap(True)
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.hide()

        self._container = QWidget()
        self._container_layout = QVBoxLayout(self._container)
        self._container_layout.setContentsMargins(0, 0, 0, 0)
        self._container_layout.setSpacing(6)

        self.add_content(self._empty_label)
        self.add_content(self._container)

        self._rows: list[QWidget] = []

    def update(self, data: Any) -> None:
        """Update with dashboard data."""
        muscles = getattr(data, "priority_muscles", []) or []

        if not muscles:
            self._container.hide()
            self._empty_label.show()
            return

        self._empty_label.hide()
        self._container.show()

        for row in self._rows:
            row.deleteLater()
        self._rows.clear()

        for muscle in muscles[:6]:
            row = self._build_muscle_row(muscle)
            self._container_layout.addWidget(row)
            self._rows.append(row)

        self._container_layout.addStretch()

    def _build_muscle_row(self, muscle: Any) -> QWidget:
        # Extract fields — muscle can be a MuscleAnalysisResult or dict
        if hasattr(muscle, "display_name"):
            name = muscle.display_name or "Unknown"
            current_sets = getattr(muscle, "current_sets", 0) or 0
            target_min = getattr(muscle, "recommended_min_sets", 0) or 0
            target_max = getattr(muscle, "recommended_max_sets", 0) or 0
            status_val = getattr(muscle, "status", "optimal")
            if hasattr(status_val, "value"):
                status_val = status_val.value
            recovery = getattr(muscle, "recovery_status", "") or ""
            progress = getattr(muscle, "progress", "") or "Stable"
            weakness = getattr(muscle, "weakness", "") or ""
        else:
            name = muscle.get("display_name", str(muscle))
            muscle_data = muscle if isinstance(muscle, dict) else {}
            current_sets = muscle_data.get("current_sets", 0) or 0
            target_min = muscle_data.get("recommended_min_sets", 0) or 0
            target_max = muscle_data.get("recommended_max_sets", 0) or 0
            status_val = muscle_data.get("status", "optimal") or "optimal"
            recovery = muscle_data.get("recovery_status", "") or ""
            progress = muscle_data.get("progress", "") or "Stable"
            weakness = muscle_data.get("weakness", "") or ""

        status_str = status_val.lower() if isinstance(status_val, str) else str(status_val).lower()
        color = STATUS_COLORS.get(status_str, "#94A3B8")
        trend_icon = TREND_ICONS.get(progress, "→")
        trend_color = TREND_COLORS.get(progress, "#94A3B8")

        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 4, 0, 4)
        row_layout.setSpacing(8)

        # Status dot
        dot = QLabel("●")
        dot.setStyleSheet(f"color: {color}; font-size: 14px;")
        dot.setFixedWidth(16)
        row_layout.addWidget(dot)

        # Info column
        info_col = QVBoxLayout()
        info_col.setContentsMargins(0, 0, 0, 0)
        info_col.setSpacing(2)

        # Name + sets + target
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(6)

        name_label = QLabel(name)
        name_label.setStyleSheet("color: #F1F5F9; font-size: 13px; font-weight: 600;")
        header_layout.addWidget(name_label)

        sets_label = QLabel(f"{current_sets:.0f}s / {target_min:.0f}-{target_max:.0f}")
        sets_label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 600;")
        header_layout.addWidget(sets_label)

        # Trend
        trend_label = QLabel(trend_icon)
        trend_label.setStyleSheet(f"color: {trend_color}; font-size: 14px; font-weight: 700;")
        header_layout.addWidget(trend_label)

        header_layout.addStretch()
        info_col.addWidget(header)

        # Recovery
        if recovery:
            recov_color = "#4ADE80"
            rl = recovery.lower()
            if "overtrain" in rl or "reduce" in rl:
                recov_color = "#F87171"
            elif "limit" in rl or "adequate" in rl:
                recov_color = "#FBBF24"
            recov_label = QLabel(recovery)
            recov_label.setStyleSheet(f"color: {recov_color}; font-size: 11px;")
            recov_label.setWordWrap(True)
            info_col.addWidget(recov_label)

        # Recommendation from weakness
        if weakness and status_str not in ("optimal", "maintenance"):
            rec_label = QLabel(weakness[:80])
            rec_label.setStyleSheet("color: #94A3B8; font-size: 11px;")
            rec_label.setWordWrap(True)
            info_col.addWidget(rec_label)

        row_layout.addLayout(info_col, 1)

        return row
