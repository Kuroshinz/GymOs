from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.command_center.models import RecoveryOverviewData
from ui.command_center.theme import Font
from ui.command_center.visualization.progress_ring import ProgressRing
from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class RecoveryOverviewWidget(DashboardCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="Recovery Overview", parent=parent)
        self._build_ui()

    def _build_ui(self) -> None:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(16)

        self._ring = ProgressRing(size=80)
        row.addWidget(self._ring)

        info = QVBoxLayout()
        info.setSpacing(2)
        self._level_label = QLabel("")
        self._level_label.setStyleSheet(Font.TITLE)
        info.addWidget(self._level_label)
        self._trend_label = QLabel("")
        self._trend_label.setStyleSheet(Font.MUTED)
        info.addWidget(self._trend_label)
        self._action_label = QLabel("")
        self._action_label.setStyleSheet(Font.CAPTION)
        self._action_label.setWordWrap(True)
        info.addWidget(self._action_label)

        row.addLayout(info, 1)
        self.add_layout(row)

        metrics = QHBoxLayout()
        metrics.setSpacing(12)
        self._sleep_label = self._make_metric("Sleep")
        self._stress_label = self._make_metric("Stress")
        self._fatigue_label = self._make_metric("Fatigue")
        metrics.addWidget(self._sleep_label)
        metrics.addWidget(self._stress_label)
        metrics.addWidget(self._fatigue_label)
        metrics.addStretch()
        self.add_layout(metrics)

    def _make_metric(self, label: str) -> QFrame:
        frame = QFrame()
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)
        val = QLabel("--")
        val.setStyleSheet(Font.STAT_VALUE)
        layout.addWidget(val)
        lbl = QLabel(label)
        lbl.setStyleSheet(Font.STAT_LABEL)
        layout.addWidget(lbl)
        return frame

    def _set_metric(self, frame: QFrame, value: str) -> None:
        labels = frame.findChildren(QLabel)
        if labels:
            labels[0].setText(value)

    def set_data(self, data: RecoveryOverviewData) -> None:
        self._ring.set_progress(value=data.score, target=1.0, label="Recovery")
        self._level_label.setText(f"Level: {data.level}")
        self._trend_label.setText(f"Trend: {data.trend}")
        self._action_label.setText("")
        self._set_metric(self._sleep_label, f"{data.sleep_score:.0%}" if data.sleep_score else "--")
        self._set_metric(self._stress_label, f"{data.stress_score:.0%}" if data.stress_score else "--")
        self._set_metric(self._fatigue_label, f"{data.fatigue_score:.0%}" if data.fatigue_score else "--")
