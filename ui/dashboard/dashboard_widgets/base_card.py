from __future__ import annotations

from typing import Any
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.components.app_card import AppCard

class DashboardCard(AppCard):
    """Adapter card for dashboard widgets, inheriting from AppCard."""

    def __init__(self, title: str = "", badge: str = "", parent: QFrame | None = None) -> None:
        super().__init__(title=title, badge=badge, parent=parent)

    def add_content(self, widget: Any) -> None:
        self._body.addWidget(widget)

    def add_layout(self, layout: Any) -> None:
        self._body.addLayout(layout)

    def set_badge(self, text: str) -> None:
        pass

    @staticmethod
    def make_row(label: str, value: str, value_color: str = "#F1F5F9") -> QFrame:
        colors = color_from_scheme(ColorScheme.DARK)
        row = QFrame()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 2, 0, 2)
        row_layout.setSpacing(8)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {colors.text_secondary}; font-size: 13px; background: transparent;")
        lbl.setFixedWidth(140)
        row_layout.addWidget(lbl)

        val = QLabel(value)
        val.setStyleSheet(f"color: {value_color}; font-size: 13px; font-weight: 600;")
        val.setWordWrap(True)
        row_layout.addWidget(val, 1)

        return row

    @staticmethod
    def make_separator() -> QFrame:
        colors = color_from_scheme(ColorScheme.DARK)
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {colors.border}; border: none;")
        return sep

    @staticmethod
    def status_color(severity: str) -> str:
        colors = color_from_scheme(ColorScheme.DARK)
        if severity in ("critical", "very_high", "high"):
            return colors.error
        if severity in ("warning", "moderate"):
            return colors.warning
        if severity in ("ok", "low"):
            return colors.success
        return colors.text_secondary
