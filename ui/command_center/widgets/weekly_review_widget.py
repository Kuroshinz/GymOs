from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.command_center.models import WeeklyReviewData
from ui.command_center.theme import C, Font
from ui.command_center.visualization.confidence_indicator import ConfidenceBar
from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class WeeklyReviewWidget(DashboardCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="Weekly Review", parent=parent)
        self._build_ui()

    def _build_ui(self) -> None:
        metrics = QHBoxLayout()
        metrics.setSpacing(8)
        self._volume_label = self._make_metric("Volume")
        self._sessions_label = self._make_metric("Sessions")
        self._prs_label = self._make_metric("PRs")
        self._recovery_label = self._make_metric("Recovery")
        metrics.addWidget(self._volume_label)
        metrics.addWidget(self._sessions_label)
        metrics.addWidget(self._prs_label)
        metrics.addWidget(self._recovery_label)
        metrics.addStretch()
        self.add_layout(metrics)

        self._adherence_bar = ConfidenceBar("Adherence")
        self.add_content(self._adherence_bar)

        self._notes_list = QVBoxLayout()
        self._notes_list.setContentsMargins(0, 4, 0, 0)
        self._notes_list.setSpacing(2)
        self.add_layout(self._notes_list)

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

    def set_data(self, data: WeeklyReviewData) -> None:
        self._set_metric(self._volume_label, f"{data.total_volume:.0f} kg" if data.total_volume else "--")
        self._set_metric(self._sessions_label, f"{data.sessions_completed}/{data.total_sessions}" if data.total_sessions else "--")
        self._set_metric(self._prs_label, str(data.prs_set) if data.prs_set else "0")
        self._set_metric(self._recovery_label, f"{data.recovery_avg:.0%}" if data.recovery_avg else "--")
        self._adherence_bar.set_score(data.adherence_rate)

        self._clear_notes()
        for note in data.notes:
            lbl = QLabel(f"• {note}")
            lbl.setStyleSheet(f"color: {C.TEXT_SECONDARY}; font-size: 12px;")
            self._notes_list.addWidget(lbl)

    def _clear_notes(self) -> None:
        for i in reversed(range(self._notes_list.count())):
            item = self._notes_list.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
