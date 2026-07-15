from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme, resolve_alpha
from ui.design_system.tokens.radius import RadiusTokens
from ui.design_system.tokens.spacing import SpacingTokens
from ui.design_system.tokens.typography import TypographyTokens, font_style

SPACE = SpacingTokens()
R = RadiusTokens()
T = TypographyTokens()


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
        text_area.setSpacing(4)

        self._title_label = QLabel(title)
        self._title_label.setStyleSheet(
            f"color: {colors.text_primary}; {font_style('h2')}; "
            f"font-size: 22px; "
            f"letter-spacing: -0.03em; background: transparent; border: none;"
        )
        text_area.addWidget(self._title_label)

        if subtitle:
            self._subtitle_label = QLabel(subtitle)
            self._subtitle_label.setStyleSheet(
                f"color: {colors.text_secondary}; font-size: 14px; "
                f"font-weight: 400; letter-spacing: 0em; "
                f"background: transparent; border: none;"
            )
            text_area.addWidget(self._subtitle_label)

        layout.addLayout(text_area)
        layout.addStretch()

        if action_text:
            btn = QPushButton(action_text)
            btn.setStyleSheet(
                f"QPushButton {{"
                f"  background-color: transparent;"
                f"  color: {colors.primary};"
                f"  border: 1px solid {resolve_alpha(colors.primary, 0.15)};"
                f"  border-radius: {R.lg};"
                f"  padding: 8px 18px;"
                f"  font-size: 13px;"
                f"  font-weight: 600;"
                f"  letter-spacing: 0.01em;"
                f"}}"
                f"QPushButton:hover {{"
                f"  background-color: {resolve_alpha(colors.primary, 0.08)};"
                f"  border-color: {resolve_alpha(colors.primary, 0.3)};"
                f"}}"
            )
            btn.setCursor(Qt.PointingHandCursor)
            if on_action:
                btn.clicked.connect(on_action)
            layout.addWidget(btn)

    def set_title(self, title: str) -> None:
        if hasattr(self, '_title_label'):
            self._title_label.setText(title)

    def set_subtitle(self, subtitle: str) -> None:
        if hasattr(self, '_subtitle_label'):
            self._subtitle_label.setText(subtitle)
