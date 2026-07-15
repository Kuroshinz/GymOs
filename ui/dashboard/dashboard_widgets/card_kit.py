"""Shared building blocks for the redesigned dashboard cards.

Provides a consistent premium ``PanelCard`` (rounded surface with an
optional titled header + action link) and small label helpers so the
individual overview widgets stay focused on their content.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ui.design_system.tokens.color import ColorScheme, color_from_scheme, resolve_alpha

C = color_from_scheme(ColorScheme.DARK)


def qcolor(hex_color: str, alpha: float = 1.0) -> QColor:
    """Build a QColor from a ``#hex`` string with an optional 0..1 alpha.

    Needed because ``resolve_alpha`` returns a CSS ``rgba()`` string that
    QColor cannot parse (it renders black in QPainter).
    """
    color = QColor(hex_color)
    color.setAlphaF(max(0.0, min(alpha, 1.0)))
    return color


def make_label(
    text: str = "",
    *,
    size: int = 13,
    weight: int = 400,
    color: str | None = None,
    letter_spacing: str = "",
    uppercase: bool = False,
) -> QLabel:
    lbl = QLabel(text.upper() if uppercase else text)
    ls = f"letter-spacing: {letter_spacing};" if letter_spacing else ""
    lbl.setStyleSheet(
        f"color: {color or C.text_primary}; font-size: {size}px; "
        f"font-weight: {weight}; background: transparent; {ls}"
    )
    return lbl


def make_chip(text: str, color: str, *, subtle: bool = True) -> QLabel:
    """Small pill/badge label."""
    bg = resolve_alpha(color, 0.16) if subtle else color
    fg = color if subtle else "#FFFFFF"
    chip = QLabel(text)
    chip.setStyleSheet(
        f"background: {bg}; color: {fg}; border-radius: 8px; "
        f"padding: 2px 9px; font-size: 11px; font-weight: 600;"
    )
    chip.setAlignment(Qt.AlignCenter)
    return chip


class ClickableLabel(QLabel):
    clicked = Signal()

    def __init__(self, text: str = "", parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class PanelCard(QFrame):
    """Rounded surface card with an optional titled header + action link."""

    action_clicked = Signal()

    def __init__(
        self,
        title: str = "",
        *,
        badge: str = "",
        action: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("PanelCard")
        self.setStyleSheet(
            f"""
            QFrame#PanelCard {{
                background-color: {C.surface};
                border: 1px solid {C.border};
                border-radius: 20px;
            }}
            """
        )
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(34)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(_shadow_color())
        self.setGraphicsEffect(shadow)

        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(22, 20, 22, 20)
        self._root.setSpacing(16)

        if title:
            header = QHBoxLayout()
            header.setContentsMargins(0, 0, 0, 0)
            header.setSpacing(8)

            title_lbl = make_label(title, size=16, weight=700, color=C.text_primary)
            header.addWidget(title_lbl)

            if badge:
                header.addWidget(make_chip(badge, C.primary))

            header.addStretch()

            if action:
                self._action = ClickableLabel(action)
                self._action.setStyleSheet(
                    f"color: {C.text_link}; font-size: 12px; font-weight: 600; "
                    f"background: transparent;"
                )
                self._action.clicked.connect(self.action_clicked.emit)
                header.addWidget(self._action)

            self._root.addLayout(header)

        self.body = QVBoxLayout()
        self.body.setContentsMargins(0, 0, 0, 0)
        self.body.setSpacing(12)
        self._root.addLayout(self.body)

    def add_widget(self, widget: QWidget, stretch: int = 0) -> None:
        self.body.addWidget(widget, stretch)

    def add_layout(self, layout) -> None:
        self.body.addLayout(layout)

    def add_stretch(self) -> None:
        self.body.addStretch()


def _shadow_color():
    from PySide6.QtGui import QColor
    return QColor(0, 0, 0, 120)
