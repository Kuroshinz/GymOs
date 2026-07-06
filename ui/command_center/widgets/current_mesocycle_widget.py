from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.command_center.models import CurrentMesocycleData
from ui.command_center.theme import Font
from ui.command_center.visualization.progress_ring import ProgressRing
from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class CurrentMesocycleWidget(DashboardCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="Current Mesocycle", parent=parent)
        self._build_ui()

    def _build_ui(self) -> None:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(16)

        self._ring = ProgressRing(size=70)
        row.addWidget(self._ring)

        info = QVBoxLayout()
        info.setSpacing(2)
        self._name_label = QLabel("--")
        self._name_label.setStyleSheet(Font.TITLE)
        info.addWidget(self._name_label)
        self._goal_label = QLabel("")
        self._goal_label.setStyleSheet(Font.MUTED)
        info.addWidget(self._goal_label)
        self._focus_label = QLabel("")
        self._focus_label.setStyleSheet(Font.CAPTION)
        info.addWidget(self._focus_label)
        row.addLayout(info, 1)
        self.add_layout(row)

        metrics = QHBoxLayout()
        metrics.setSpacing(12)
        self._week_label = self._make_metric("Week")
        self._phase_label = self._make_metric("Phase")
        self._deload_label = self._make_metric("Next Deload")
        metrics.addWidget(self._week_label)
        metrics.addWidget(self._phase_label)
        metrics.addWidget(self._deload_label)
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

    def set_data(self, data: CurrentMesocycleData) -> None:
        self._name_label.setText(data.name or "No active mesocycle")
        self._goal_label.setText(f"Goal: {data.goal}" if data.goal else "")
        self._focus_label.setText(f"Focus: {data.focus}" if data.focus else "")
        self._ring.set_progress(value=data.week, target=data.total_weeks, label="Weeks")
        self._set_metric(self._week_label, f"{data.week}/{data.total_weeks}")
        self._set_metric(self._phase_label, data.phase)
        self._set_metric(self._deload_label, f"in {data.next_deload_in} wk" if data.next_deload_in else "--")
