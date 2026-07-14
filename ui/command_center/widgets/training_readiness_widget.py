from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.command_center.models import TrainingReadinessData
from ui.command_center.theme import C, Font
from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class TrainingReadinessWidget(DashboardCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="Training Readiness", parent=parent)
        self._build_ui()

    def _build_ui(self) -> None:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(12)

        self._readiness_label = QLabel("--")
        self._readiness_label.setStyleSheet("font-size: 36px; font-weight: 800;")
        row.addWidget(self._readiness_label)

        info = QVBoxLayout()
        info.setSpacing(2)
        self._score_label = QLabel("")
        self._score_label.setStyleSheet(Font.MUTED)
        info.addWidget(self._score_label)
        self._factor_label = QLabel("")
        self._factor_label.setStyleSheet(Font.CAPTION)
        info.addWidget(self._factor_label)
        row.addLayout(info, 1)
        self.add_layout(row)

        self._recs_list = QVBoxLayout()
        self._recs_list.setContentsMargins(0, 8, 0, 0)
        self._recs_list.setSpacing(2)
        self.add_layout(self._recs_list)

    def set_data(self, data: TrainingReadinessData) -> None:
        readiness = data.readiness or "unknown"
        score = data.score or 0.0

        color = C.TEXT_SUCCESS if readiness in ("ready", "optimal") else C.TEXT_WARN if readiness in ("moderate", "fair") else C.TEXT_DANGER
        self._readiness_label.setStyleSheet(f"font-size: 36px; font-weight: 800; color: {color};")
        self._readiness_label.setText(readiness.title())
        self._score_label.setText(f"Score: {score:.0%}")
        self._factor_label.setText(f"Limiting Factor: {data.limiting_factor}" if data.limiting_factor else "")

        self._clear_recs()
        for rec in data.recommendations:
            lbl = QLabel(f"• {rec}")
            lbl.setStyleSheet(f"color: {C.TEXT_SECONDARY}; font-size: 12px;")
            self._recs_list.addWidget(lbl)

    def _clear_recs(self) -> None:
        for _i in reversed(range(self._recs_list.count())):
            item = self._recs_list.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
