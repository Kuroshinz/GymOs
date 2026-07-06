from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.command_center.models import IntentData
from ui.command_center.theme import Font
from ui.command_center.visualization.progress_ring import ProgressRing
from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class IntentCardWidget(DashboardCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="Current Intent", parent=parent)
        self._build_ui()

    def _build_ui(self) -> None:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(16)

        self._ring = ProgressRing(size=80)
        row.addWidget(self._ring)

        info = QVBoxLayout()
        info.setSpacing(4)

        self._goal_label = QLabel("No active goal")
        self._goal_label.setStyleSheet(Font.TITLE)
        self._goal_label.setWordWrap(True)
        info.addWidget(self._goal_label)

        self._target_label = QLabel("")
        self._target_label.setStyleSheet(Font.MUTED)
        info.addWidget(self._target_label)

        self._phase_label = QLabel("")
        self._phase_label.setStyleSheet(Font.CAPTION)
        info.addWidget(self._phase_label)

        row.addLayout(info, 1)
        self.add_layout(row)

        metrics = QHBoxLayout()
        metrics.setSpacing(16)
        self._rate_label = self._make_metric("Weekly Rate")
        self._adherence_label = self._make_metric("Adherence")
        metrics.addWidget(self._rate_label)
        metrics.addWidget(self._adherence_label)
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

    def update_data(self, data: object) -> None:
        intent = getattr(data, "intent_data", None)
        if intent is not None:
            self.set_data(intent)

    def set_data(self, data: IntentData) -> None:
        self._goal_label.setText(data.current_goal or "No active goal")
        if data.target_date:
            self._target_label.setText(f"Target: {data.target_date}")
        else:
            self._target_label.setText("")
        self._phase_label.setText(f"Phase: {data.phase}" if data.phase else "")
        self._ring.set_progress(
            value=data.progress_percent,
            target=100.0,
            label="Progress",
        )
        self._set_metric(self._rate_label, f"{data.weekly_rate:.2f}/wk" if data.weekly_rate else "--")
        self._set_metric(self._adherence_label, f"{data.adherence:.0%}" if data.adherence else "--")
