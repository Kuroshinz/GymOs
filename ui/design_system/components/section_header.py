from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.spacing import SpacingTokens

SPACE = SpacingTokens()


class SectionHeader(QFrame):
    def __init__(
        self,
        title: str,
        subtitle: str = "",
        action_text: str = "",
        on_action: Callable[[], None] | None = None,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._build_ui(title, subtitle, action_text, on_action)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _build_ui(self, title: str, subtitle: str, action_text: str, on_action: Callable | None) -> None:
        colors = self._colors()
        self.setStyleSheet("SectionHeader { background: transparent; border: none; }")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        text_area = QVBoxLayout()
        text_area.setSpacing(2)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 18px; font-weight: 700; "
            f"letter-spacing: -0.02em; background: transparent; border: none;"
        )
        text_area.addWidget(title_label)

        if subtitle:
            sub = QLabel(subtitle)
            sub.setStyleSheet(
                f"color: {colors.text_secondary}; font-size: 13px; "
                f"background: transparent; border: none;"
            )
            text_area.addWidget(sub)

        layout.addLayout(text_area)
        layout.addStretch()

        if action_text:
            btn = QPushButton(action_text)
            btn.setStyleSheet(
                f"QPushButton {{"
                f"  background-color: transparent;"
                f"  color: {colors.primary};"
                f"  border: 1px solid {colors.border};"
                f"  border-radius: 6px;"
                f"  padding: 6px 14px;"
                f"  font-size: 13px;"
                f"  font-weight: 500;"
                f"}}"
                f"QPushButton:hover {{"
                f"  background-color: {colors.surface_hover};"
                f"  border-color: {colors.primary};"
                f"}}"
            )
            btn.setCursor(Qt.PointingHandCursor)
            if on_action:
                btn.clicked.connect(on_action)
            layout.addWidget(btn)

    def set_title(self, title: str) -> None:
        pass

    def set_subtitle(self, subtitle: str) -> None:
        pass
