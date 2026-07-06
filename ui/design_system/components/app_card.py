from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.elevation import ElevationTokens, apply_elevation
from ui.design_system.tokens.radius import RadiusTokens
from ui.design_system.tokens.spacing import SpacingTokens

RADIUS = RadiusTokens()
SPACE = SpacingTokens()
ELEVATION = ElevationTokens()


class AppCard(QFrame):
    clicked = Signal()

    def __init__(
        self,
        title: str = "",
        subtitle: str = "",
        badge: str = "",
        elevated: bool = True,
        interactive: bool = False,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._interactive = interactive
        self._color_scheme = ColorScheme.DARK
        self._build_ui(title, subtitle, badge, elevated)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _build_ui(self, title: str, subtitle: str, badge: str, elevated: bool) -> None:
        colors = self._colors()

        if elevated:
            apply_elevation(self, 2, is_dark=True, bg_color=colors.surface)

        style = f"""
            AppCard {{
                background-color: {colors.surface};
                border-radius: {RADIUS.lg};
                border: 1px solid {colors.border};
            }}
        """
        if self._interactive:
            style += f"""
                AppCard:hover {{
                    border-color: {colors.border_hover};
                    background-color: {colors.surface_hover};
                }}
            """
        self.setStyleSheet(style)
        self.setCursor(Qt.PointingHandCursor if self._interactive else Qt.ArrowCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        if title:
            header = QHBoxLayout()
            header.setContentsMargins(0, 0, 0, 0)
            header.setSpacing(8)

            title_label = QLabel(title.upper())
            title_label.setStyleSheet(
                f"color: {colors.text_secondary}; font-size: 11px; font-weight: 600; "
                f"letter-spacing: 0.5px; text-transform: uppercase;"
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
            layout.addLayout(header)

        if subtitle:
            sub = QLabel(subtitle)
            sub.setStyleSheet(f"color: {colors.text_primary}; font-size: 13px; font-weight: 500;")
            sub.setWordWrap(True)
            layout.addWidget(sub)

        self._body = QVBoxLayout()
        self._body.setContentsMargins(0, 0, 0, 0)
        self._body.setSpacing(8)
        layout.addLayout(self._body)

    def add_content(self, widget: QWidget) -> None:
        self._body.addWidget(widget)

    def add_layout(self, layout: Any) -> None:
        self._body.addLayout(layout)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self._interactive:
            self.clicked.emit()

    def set_color_scheme(self, scheme: ColorScheme) -> None:
        self._color_scheme = scheme

    @staticmethod
    def make_row(label: str, value: str, value_color: str | None = None) -> QFrame:
        from PySide6.QtWidgets import QHBoxLayout
        colors = color_from_scheme(ColorScheme.DARK)
        row = QFrame()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 2, 0, 2)
        row_layout.setSpacing(8)

        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {colors.text_secondary}; font-size: 13px;")
        lbl.setFixedWidth(140)
        row_layout.addWidget(lbl)

        val = QLabel(value)
        vc = value_color or colors.text_primary
        val.setStyleSheet(f"color: {vc}; font-size: 13px; font-weight: 600;")
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
