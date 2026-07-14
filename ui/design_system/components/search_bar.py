from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens
from ui.design_system.tokens.spacing import SpacingTokens

RADIUS = RadiusTokens()
SPACE = SpacingTokens()


class SearchBar(QFrame):
    text_changed = Signal(str)
    search_submitted = Signal(str)

    def __init__(
        self,
        placeholder: str = "Search...",
        shortcut_hint: str = "",
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._build_ui(placeholder, shortcut_hint)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _build_ui(self, placeholder: str, shortcut_hint: str) -> None:
        colors = self._colors()
        self.setFixedHeight(36)
        self.setStyleSheet(f"""
            SearchBar {{
                background-color: {colors.surface};
                border-radius: {RADIUS.md};
                border: 1px solid {colors.border};
            }}
            SearchBar:focus-within {{
                border-color: {colors.primary};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        icon_label = QLabel("\U0001F50D")
        icon_label.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 14px; background: transparent; border: none;"
        )
        layout.addWidget(icon_label)

        self._input = QLineEdit()
        self._input.setAccessibleName("Search input")
        self._input.setToolTip(placeholder)
        self._input.setPlaceholderText(placeholder)
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {colors.text_primary};
                font-size: 13px;
                font-weight: 400;
            }}
            QLineEdit::placeholder {{
                color: {colors.text_disabled};
            }}
        """)
        self._input.textChanged.connect(self.text_changed.emit)
        self._input.returnPressed.connect(lambda: self.search_submitted.emit(self._input.text()))
        layout.addWidget(self._input, 1)

        if shortcut_hint:
            hint = QLabel(shortcut_hint)
            hint.setStyleSheet(
                f"color: {colors.text_disabled}; font-size: 11px; "
                f"background: {colors.surface_hover}; border-radius: 4px; "
                f"padding: 2px 6px;"
            )
            layout.addWidget(hint)

    def set_text(self, text: str) -> None:
        self._input.setText(text)

    def text(self) -> str:
        return self._input.text()

    def clear(self) -> None:
        self._input.clear()
