from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.command_center.models import ProductStateData
from ui.command_center.theme import Font
from ui.command_center.visualization.progress_ring import ProgressRing
from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class ProductStateWidget(DashboardCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="Product State", parent=parent)
        self._build_ui()

    def _build_ui(self) -> None:
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(16)

        self._ring = ProgressRing(size=70)
        row.addWidget(self._ring)

        info = QVBoxLayout()
        info.setSpacing(2)
        self._version_label = QLabel("--")
        self._version_label.setStyleSheet(Font.TITLE)
        info.addWidget(self._version_label)
        self._phase_label = QLabel("")
        self._phase_label.setStyleSheet(Font.MUTED)
        info.addWidget(self._phase_label)
        self._rfc_label = QLabel("")
        self._rfc_label.setStyleSheet(Font.CAPTION)
        info.addWidget(self._rfc_label)
        row.addLayout(info, 1)
        self.add_layout(row)

        metrics = QHBoxLayout()
        metrics.setSpacing(8)
        self._caps_label = self._make_metric("Capabilities Active")
        self._tests_label = self._make_metric("Tests Passing")
        metrics.addWidget(self._caps_label)
        metrics.addWidget(self._tests_label)
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

    def set_data(self, data: ProductStateData) -> None:
        self._version_label.setText(f"v{data.version}" if data.version else "--")
        self._phase_label.setText(f"Phase: {data.release_phase}" if data.release_phase else "")
        self._rfc_label.setText(f"Current RFC: {data.current_rfc}" if data.current_rfc else "")
        self._ring.set_progress(value=data.passing_tests, target=data.total_tests, label="Tests")
        self._set_metric(self._caps_label, f"{data.capabilities_active}/{data.total_capabilities}" if data.total_capabilities else "--")
        self._set_metric(self._tests_label, f"{data.passing_tests}/{data.total_tests}" if data.total_tests else "--")
