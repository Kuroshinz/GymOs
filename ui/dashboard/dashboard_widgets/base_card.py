from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens
from ui.design_system.tokens.spacing import SpacingTokens

R = RadiusTokens()
S = SpacingTokens()


class DashboardCard(QFrame):
    CARD_STYLE = None
    TITLE_STYLE = None
    BADGE_STYLE = None

    def __init__(self, title: str = "", badge: str = "", parent: QFrame | None = None) -> None:
        super().__init__(parent)
        self._color_scheme = ColorScheme.DARK
        self._apply_styles(title, badge)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _apply_styles(self, title: str, badge: str) -> None:
        colors = self._colors()
        self.setStyleSheet(f"""
            DashboardCard {{
                background-color: {colors.surface};
                border-radius: {R.lg};
                border: 1px solid {colors.border};
            }}
        """)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 16, 20, 16)
        self._layout.setSpacing(12)

        if title:
            header = QHBoxLayout()
            header.setContentsMargins(0, 0, 0, 0)
            header.setSpacing(8)

            title_label = QLabel(title.upper())
            title_label.setStyleSheet(
                f"color: {colors.text_secondary}; font-size: 11px; font-weight: 600; "
                f"letter-spacing: 0.5px; text-transform: uppercase; background: transparent;"
            )
            header.addWidget(title_label)

            if badge:
                badge_label = QLabel(badge)
                badge_label.setStyleSheet(
                    f"background-color: {colors.border}; color: {colors.text_secondary}; "
                    f"border-radius: 8px; padding: 2px 8px; font-size: 11px;"
                )
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
