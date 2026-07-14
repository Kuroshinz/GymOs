from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from ui.command_center.models import CapabilityProgressData
from ui.command_center.theme import C, Font
from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class CapabilityProgressWidget(DashboardCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="Capability Progress", parent=parent)
        self._build_ui()

    def _build_ui(self) -> None:
        metrics = QHBoxLayout()
        metrics.setSpacing(8)
        self._total_label = self._make_metric("Total")
        self._complete_label = self._make_metric("Complete")
        self._in_progress_label = self._make_metric("In Progress")
        self._blocked_label = self._make_metric("Blocked")
        metrics.addWidget(self._total_label)
        metrics.addWidget(self._complete_label)
        metrics.addWidget(self._in_progress_label)
        metrics.addWidget(self._blocked_label)
        metrics.addStretch()
        self.add_layout(metrics)

        self._health_bar = QProgressBar()
        self._health_bar.setFixedHeight(8)
        self._health_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {C.BORDER};
                border: none;
                border-radius: 4px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {C.ACCENT};
                border-radius: 4px;
            }}
        """)
        self.add_content(self._health_bar)

        self._cap_list = QVBoxLayout()
        self._cap_list.setContentsMargins(0, 4, 0, 0)
        self._cap_list.setSpacing(2)
        self.add_layout(self._cap_list)

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

    def set_data(self, data: CapabilityProgressData) -> None:
        self._set_metric(self._total_label, str(data.total))
        self._set_metric(self._complete_label, str(data.complete))
        self._set_metric(self._in_progress_label, str(data.in_progress))
        self._set_metric(self._blocked_label, str(data.blocked))
        self._health_bar.setValue(int(data.overall_health) if data.overall_health else 0)
        self._health_bar.setFormat(f"Health: {data.overall_health:.0f}%" if data.overall_health else "")

        self._clear_cap_list()
        for cap in data.capabilities[:6]:
            row = QFrame()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 2, 0, 2)
            row_layout.setSpacing(6)
            name = QLabel(cap.get("name", ""))
            name.setStyleSheet(f"color: {C.TEXT_SECONDARY}; font-size: 12px;")
            name.setFixedWidth(160)
            row_layout.addWidget(name)
            status = QLabel(cap.get("status", "").title())
            status_color = C.TEXT_SUCCESS if cap.get("status") in ("complete", "ready") else C.TEXT_WARN if cap.get("status") in ("in_progress", "active") else C.TEXT_DANGER
            status.setStyleSheet(f"color: {status_color}; font-size: 11px; font-weight: 600;")
            row_layout.addWidget(status)
            health = QLabel(f"Health: {cap.get('health', 0):.0f}")
            health.setStyleSheet(Font.CAPTION)
            row_layout.addWidget(health)
            row_layout.addStretch()
            self._cap_list.addWidget(row)

    def _clear_cap_list(self) -> None:
        for _i in reversed(range(self._cap_list.count())):
            item = self._cap_list.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
