"""Goal progress card — displays current weight, goal, remaining, estimated weeks, gain rate, progress bar."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout

from .base_card import DashboardCard


class GoalProgressWidget(DashboardCard):
    """Shows current weight vs goal weight progress.

    Fields:
      - Current Weight (large)
      - Goal Weight
      - Remaining Weight
      - Estimated Weeks Remaining
      - Weekly Gain Rate
      - Lean Bulk Quality
      - Progress Bar (% toward goal)
    """

    WEIGHT_STYLE = "color: #F1F5F9; font-size: 42px; font-weight: 800;"
    WEIGHT_UNIT_STYLE = "color: #64748B; font-size: 18px; font-weight: 600; margin-left: 4px;"
    LABEL_STYLE = "color: #64748B; font-size: 13px;"
    VALUE_STYLE = "color: #F1F5F9; font-size: 15px; font-weight: 600;"
    EMPHASIS_STYLE = "color: #4ADE80; font-size: 15px; font-weight: 700;"
    BAR_BG_STYLE = "background-color: #334155; border-radius: 6px;"
    BAR_FILL_STYLE = "background-color: #818CF8; border-radius: 6px;"
    PLACEHOLDER_STYLE = "color: #64748B; font-size: 14px; padding: 24px 0px;"

    def __init__(self, parent: QFrame | None = None) -> None:
        super().__init__(title="Goal Progress", parent=parent)
        self._data: Any = None
        self._container = QVBoxLayout()
        self._container.setContentsMargins(0, 0, 0, 0)
        self._container.setSpacing(12)
        self._show_placeholder()
        self.add_layout(self._container)

    def _show_placeholder(self) -> None:
        self._clear()
        placeholder = QLabel(
            "No body weight data yet.\nLog your first weight to track progress."
        )
        placeholder.setStyleSheet(self.PLACEHOLDER_STYLE)
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setWordWrap(True)
        self._container.addWidget(placeholder)

    def _clear(self) -> None:
        for i in reversed(range(self._container.count())):
            item = self._container.takeAt(0)
            if item:
                w = item.widget()
                if w:
                    w.deleteLater()
                la = item.layout()
                if la:
                    while la.count():
                        c = la.takeAt(0)
                        if c.widget():
                            c.widget().deleteLater()

    def update(self, data: Any) -> None:
        """Update with dashboard data."""
        weight = getattr(data, "goal_progress_weight", 0.0) or 0.0
        target = getattr(data, "goal_progress_target", 0.0) or 0.0
        remaining = getattr(data, "goal_progress_remaining", 0.0) or 0.0
        weeks = getattr(data, "goal_progress_weeks", 0) or 0
        rate = getattr(data, "goal_progress_rate", 0.0) or 0.0
        quality = getattr(data, "goal_progress_quality", "") or ""
        percent = getattr(data, "goal_progress_percent", 0.0) or 0.0

        if weight <= 0:
            self._show_placeholder()
            return

        self._clear()

        # Current weight (large display)
        weight_row = QHBoxLayout()
        weight_row.setContentsMargins(0, 0, 0, 0)
        weight_row.setSpacing(0)

        weight_label = QLabel(f"{weight:.1f}")
        weight_label.setStyleSheet(self.WEIGHT_STYLE)
        weight_row.addWidget(weight_label)

        unit_label = QLabel("kg")
        unit_label.setStyleSheet(self.WEIGHT_UNIT_STYLE)
        unit_label.setAlignment(Qt.AlignBottom)
        unit_label.setContentsMargins(0, 0, 0, 8)
        weight_row.addWidget(unit_label)
        weight_row.addStretch()
        self._container.addLayout(weight_row)

        # Goal Weight
        self._container.addWidget(self._make_info_row("Goal Weight", f"{target:.1f} kg"))

        # Remaining
        self._container.addWidget(self._make_info_row("Remaining", f"{remaining:.1f} kg"))

        # Est. Weeks Left
        weeks_str = str(weeks) if weeks > 0 else "—"
        self._container.addWidget(self._make_info_row("Est. Weeks Left", weeks_str))

        # Weekly Gain Rate
        self._container.addWidget(self._make_info_row("Weekly Gain Rate", f"{rate:.2f} kg/wk"))

        # Lean Bulk Quality
        if quality:
            q_color = self._quality_color(quality)
            q_row = self._make_info_row("Lean Bulk Quality", quality)
            q_labels = q_row.findChildren(QLabel)
            if len(q_labels) >= 2:
                q_labels[1].setStyleSheet(f"color: {q_color}; font-size: 15px; font-weight: 700;")
            self._container.addWidget(q_row)

        # Progress bar
        bar = self._make_progress_bar(percent)
        self._container.addWidget(bar)

    def _make_info_row(self, label: str, value: str) -> QFrame:
        row = QFrame()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.setSpacing(8)
        lbl = QLabel(label)
        lbl.setStyleSheet(self.LABEL_STYLE)
        lbl.setFixedWidth(140)
        layout.addWidget(lbl)
        val = QLabel(value)
        val.setStyleSheet(self.VALUE_STYLE)
        layout.addWidget(val, 1)
        return row

    def _make_progress_bar(self, fraction: float) -> QFrame:
        container = QFrame()
        container.setFixedHeight(12)
        container.setStyleSheet(self.BAR_BG_STYLE)
        container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        clamped = min(max(fraction / 100.0, 0.0), 1.0)
        fill = QFrame(container)
        fill.setStyleSheet(self.BAR_FILL_STYLE)
        fill.setFixedHeight(12)
        fill.setFixedWidth(int(max(container.width() * clamped, 0)))

        container.installEventFilter(self)
        self._bar_fraction = clamped
        return container

    def eventFilter(self, obj: QFrame, event: object) -> bool:
        from PySide6.QtCore import QEvent

        if event.type() == QEvent.Resize and isinstance(obj, QFrame):
            fraction = getattr(self, "_bar_fraction", 0.0)
            for child in obj.findChildren(QFrame):
                if child.styleSheet() == self.BAR_FILL_STYLE:
                    child.setFixedWidth(int(max(obj.width() * fraction, 0)))
                    break
        return super().eventFilter(obj, event)

    def _quality_color(self, quality: str) -> str:
        q = quality.lower()
        if q in ("excellent", "great", "optimal"):
            return "#4ADE80"
        if q in ("good", "solid"):
            return "#818CF8"
        if q in ("fair", "average"):
            return "#FBBF24"
        if q in ("poor", "suboptimal"):
            return "#F87171"
        return "#94A3B8"
