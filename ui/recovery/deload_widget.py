"""Deload Widget — shows upcoming deload status and history."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QWidget

from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class DeloadWidget(DashboardCard):
    """Shows if a deload is due, active, or upcoming."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="DELOAD", parent=parent)

        self._status_icon = QLabel("🔄")
        self._status_icon.setStyleSheet("font-size: 32px;")
        self._status_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_content(self._status_icon)

        self._status_label = QLabel("No deload scheduled")
        self._status_label.setStyleSheet("color: #F1F5F9; font-size: 16px; font-weight: 600;")
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_content(self._status_label)

        self._detail_label = QLabel("")
        self._detail_label.setStyleSheet("color: #94A3B8; font-size: 12px;")
        self._detail_label.setWordWrap(True)
        self._detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_content(self._detail_label)

    def update_data(self, data: Any) -> None:
        active_deload = getattr(data, "recovery_active_deload", None)
        flags = getattr(data, "recovery_flags", []) or []

        deload_flags = [f for f in flags if "deload" in f.lower()]

        if deload_flags:
            self._status_icon.setText("⚠️")
            self._status_icon.setStyleSheet("font-size: 32px;")
            self._status_label.setText("Deload Recommended")
            self._status_label.setStyleSheet("color: #FB923C; font-size: 16px; font-weight: 600;")
            self._detail_label.setText(deload_flags[0])
        elif active_deload:
            self._status_icon.setText("🔄")
            self._status_icon.setStyleSheet("font-size: 32px;")
            self._status_label.setText("Deload Active")
            self._status_label.setStyleSheet("color: #A855F7; font-size: 16px; font-weight: 600;")
            end_date = getattr(active_deload, "end_date", "") if hasattr(active_deload, "end_date") else ""
            self._detail_label.setText(f"Active until {end_date}. Reduce volume by 40-60%.")
        else:
            self._status_icon.setText("✅")
            self._status_icon.setStyleSheet("font-size: 32px;")
            self._status_label.setText("No Deload Needed")
            self._status_label.setStyleSheet("color: #4ADE80; font-size: 16px; font-weight: 600;")
            self._detail_label.setText("Recovery metrics looking good.")
