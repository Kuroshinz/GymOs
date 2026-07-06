from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.command_center.models import SystemHealthData
from ui.command_center.theme import Font
from ui.command_center.visualization.progress_ring import ProgressRing
from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class SystemHealthWidget(DashboardCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="System Health", parent=parent)
        self._build_ui()

    def _build_ui(self) -> None:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(16)

        self._ring = ProgressRing(size=80)
        row.addWidget(self._ring)

        info = QVBoxLayout()
        info.setSpacing(2)
        self._rating_label = QLabel("")
        self._rating_label.setStyleSheet(Font.TITLE)
        info.addWidget(self._rating_label)
        self._score_label = QLabel("")
        self._score_label.setStyleSheet(Font.MUTED)
        info.addWidget(self._score_label)
        row.addLayout(info, 1)
        self.add_layout(row)

        scores = QHBoxLayout()
        scores.setSpacing(8)
        self._arch_label = self._make_metric("Architecture")
        self._test_label = self._make_metric("Test Coverage")
        self._doc_label = self._make_metric("Documentation")
        self._platform_label = self._make_metric("Platform")
        scores.addWidget(self._arch_label)
        scores.addWidget(self._test_label)
        scores.addWidget(self._doc_label)
        scores.addWidget(self._platform_label)
        scores.addStretch()
        self.add_layout(scores)

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

    def set_data(self, data: SystemHealthData) -> None:
        self._ring.set_progress(value=data.overall, target=100.0, label="Health")
        self._rating_label.setText(f"Rating: {data.rating.title()}" if data.rating else "Rating: --")
        self._score_label.setText(f"Overall: {data.overall:.1f}/100")
        self._set_metric(self._arch_label, f"{data.architecture:.0f}")
        self._set_metric(self._test_label, f"{data.test_coverage:.0f}")
        self._set_metric(self._doc_label, f"{data.documentation:.0f}")
        self._set_metric(self._platform_label, f"{data.platform:.0f}")
