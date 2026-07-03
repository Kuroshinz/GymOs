"""Base card widget with consistent styling for all dashboard cards."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout


class DashboardCard(QFrame):
    """Base card for all dashboard widgets.

    Provides consistent dark-theme styling with a title header.
    Subclasses call add_content() to populate the body.
    """

    CARD_STYLE = """
        DashboardCard {
            background-color: #1E293B;
            border-radius: 12px;
            border: 1px solid #334155;
        }
    """
    TITLE_STYLE = "color: #94A3B8; font-size: 11px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;"
    BADGE_STYLE = "background-color: #334155; color: #94A3B8; border-radius: 8px; padding: 2px 8px; font-size: 11px;"

    def __init__(self, title: str = "", badge: str = "", parent: QFrame | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet(self.CARD_STYLE)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 16, 20, 16)
        self._layout.setSpacing(12)

        if title:
            header = QHBoxLayout()
            header.setContentsMargins(0, 0, 0, 0)
            header.setSpacing(8)

            title_label = QLabel(title.upper())
            title_label.setStyleSheet(self.TITLE_STYLE)
            header.addWidget(title_label)

            if badge:
                badge_label = QLabel(badge)
                badge_label.setStyleSheet(self.BADGE_STYLE)
                badge_label.setFixedHeight(20)
                header.addWidget(badge_label)

            header.addStretch()
            self._layout.addLayout(header)

        self._body = QVBoxLayout()
        self._body.setContentsMargins(0, 0, 0, 0)
        self._body.setSpacing(8)
        self._layout.addLayout(self._body)

    def add_content(self, widget: Any) -> None:
        self._body.addWidget(widget)

    def add_layout(self, layout: Any) -> None:
        self._body.addLayout(layout)

    def set_badge(self, text: str) -> None:
        pass

    @staticmethod
    def make_row(label: str, value: str, value_color: str = "#F1F5F9") -> QFrame:
        row = QFrame()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 2, 0, 2)
        row_layout.setSpacing(8)

        lbl = QLabel(label)
        lbl.setStyleSheet("color: #64748B; font-size: 13px;")
        lbl.setFixedWidth(140)
        row_layout.addWidget(lbl)

        val = QLabel(value)
        val.setStyleSheet(f"color: {value_color}; font-size: 13px; font-weight: 600;")
        val.setWordWrap(True)
        row_layout.addWidget(val, 1)

        return row

    @staticmethod
    def make_separator() -> QFrame:
        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet("background-color: #334155; border: none;")
        return sep

    @staticmethod
    def status_color(severity: str) -> str:
        if severity in ("critical", "very_high", "high"):
            return "#F87171"
        if severity in ("warning", "moderate"):
            return "#FBBF24"
        if severity in ("ok", "low"):
            return "#4ADE80"
        return "#94A3B8"
