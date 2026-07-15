"""Recovery Status card — recovery ring + vitals + details action."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.dashboard.dashboard_models import DashboardData
from ui.dashboard.dashboard_widgets.card_kit import PanelCard, make_chip, make_label
from ui.design_system.tokens.color import ColorScheme, color_from_scheme, resolve_alpha
from ui.visualization.rings.recovery_ring import RecoveryRing

C = color_from_scheme(ColorScheme.DARK)

_STATUS_COLORS = {
    "optimal": C.success,
    "good": C.success,
    "low": C.warning,
    "high": C.error,
}


def ghost_button(text: str) -> QPushButton:
    btn = QPushButton(text)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setStyleSheet(
        f"""
        QPushButton {{
            background: {resolve_alpha(C.primary, 0.10)};
            color: {C.text_link};
            border: 1px solid {resolve_alpha(C.primary, 0.20)};
            border-radius: 12px;
            padding: 11px 16px;
            font-size: 13px;
            font-weight: 600;
        }}
        QPushButton:hover {{ background: {resolve_alpha(C.primary, 0.18)}; }}
        """
    )
    return btn


class RecoveryStatusWidget(PanelCard):
    view_details_clicked = Signal()

    def __init__(self, motion: Any = None, parent: QWidget | None = None) -> None:
        super().__init__(title="Recovery Status", parent=parent)
        self._motion = motion

        content = QHBoxLayout()
        content.setContentsMargins(0, 0, 0, 0)
        content.setSpacing(16)

        ring_col = QVBoxLayout()
        ring_col.setContentsMargins(0, 0, 0, 0)
        ring_col.setSpacing(6)
        self._ring = RecoveryRing(size=120, stroke_width=10)
        self._ring.setStyleSheet("background: transparent; border: none;")
        ring_col.addWidget(self._ring, 0, Qt.AlignCenter)
        self._ring_label = make_label("Good", size=12, weight=600, color=C.success)
        self._ring_label.setAlignment(Qt.AlignCenter)
        ring_col.addWidget(self._ring_label)
        content.addLayout(ring_col)

        self._vitals = QVBoxLayout()
        self._vitals.setContentsMargins(0, 4, 0, 4)
        self._vitals.setSpacing(10)
        self._vital_rows: list[QFrame] = []
        content.addLayout(self._vitals, 1)

        self.add_layout(content)

        self._button = ghost_button("\u26A1  View Recovery Details")
        self._button.clicked.connect(self.view_details_clicked.emit)
        self.add_widget(self._button)

    def set_motion_service(self, motion: Any) -> None:
        self._motion = motion

    def _clear_vitals(self) -> None:
        for row in self._vital_rows:
            row.setParent(None)
        self._vital_rows.clear()

    def update_data(self, data: DashboardData) -> None:
        self._ring.set_value(float(data.recovery_percent), 100.0)
        self._ring_label.setText(data.recovery_qualifier or "")

        self._clear_vitals()
        for vital in data.recovery_vitals:
            row = QFrame()
            row.setStyleSheet("background: transparent;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(0, 0, 0, 0)
            rl.setSpacing(8)
            rl.addWidget(make_label(vital["label"], size=13, weight=400, color=C.text_secondary))
            rl.addStretch()
            rl.addWidget(make_label(vital["value"], size=13, weight=700, color=C.text_primary))
            status = vital.get("status", "")
            color = _STATUS_COLORS.get(status.lower(), C.text_secondary)
            rl.addWidget(make_chip(status, color))
            self._vitals.addWidget(row)
            self._vital_rows.append(row)
