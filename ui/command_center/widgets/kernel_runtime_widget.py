from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.command_center.models import KernelRuntimeData
from ui.command_center.theme import C, Font
from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class KernelRuntimeWidget(DashboardCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="Kernel Runtime", parent=parent)
        self._build_ui()

    def _build_ui(self) -> None:
        grid = QVBoxLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(6)

        self._rows: dict[str, QLabel] = {}
        for field in ["Status", "Uptime", "Active Plugins", "Total Plugins", "Memory", "Event Queue", "Last Event"]:
            row = QFrame()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 2, 0, 2)
            row_layout.setSpacing(8)
            label = QLabel(field)
            label.setStyleSheet(Font.MUTED)
            label.setFixedWidth(110)
            row_layout.addWidget(label)
            value = QLabel("--")
            value.setStyleSheet(f"color: {C.TEXT_PRIMARY}; font-size: 13px; font-weight: 500;")
            row_layout.addWidget(value, 1)
            self._rows[field] = value
            grid.addWidget(row)

        self.add_layout(grid)

    def set_data(self, data: KernelRuntimeData) -> None:
        self._set("Status", data.status.title() if data.status else "--")
        self._set("Uptime", data.uptime or "--")
        self._set("Active Plugins", f"{data.active_plugins}/{data.total_plugins}" if data.total_plugins else "--")
        self._set("Total Plugins", str(data.total_plugins) if data.total_plugins else "--")
        self._set("Memory", data.memory_usage or "--")
        self._set("Event Queue", str(data.event_queue_size) if data.event_queue_size else "0")
        self._set("Last Event", data.last_event or "--")

        status_color = C.TEXT_SUCCESS if data.status == "running" else C.TEXT_WARN if data.status == "degraded" else C.TEXT_DANGER
        status_lbl = self._rows.get("Status")
        if status_lbl:
            status_lbl.setStyleSheet(f"color: {status_color}; font-size: 13px; font-weight: 600;")

    def _set(self, field: str, value: str) -> None:
        lbl = self._rows.get(field)
        if lbl:
            lbl.setText(value)
