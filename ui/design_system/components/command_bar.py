from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.elevation import ElevationTokens
from ui.design_system.tokens.radius import RadiusTokens
from ui.design_system.tokens.spacing import SpacingTokens

RADIUS = RadiusTokens()
SPACE = SpacingTokens()
ELEVATION = ElevationTokens()


class CommandBar(QFrame):
    command_selected = Signal(str)
    dismissed = Signal()

    def __init__(
        self,
        placeholder: str = "Type a command...",
        commands: Sequence[tuple[str, str]] | None = None,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._commands: list[tuple[str, str]] = list(commands or [])
        self._build_ui(placeholder)
        self.hide()

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _build_ui(self, placeholder: str) -> None:
        colors = self._colors()
        self.setStyleSheet(f"""
            CommandBar {{
                background-color: {colors.surface};
                border-radius: {RADIUS.xl};
                border: 1px solid {colors.border};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        input_frame = QFrame()
        input_frame.setStyleSheet("background: transparent; border: none;")
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(16, 12, 16, 12)

        prompt = QLabel(">")
        prompt.setStyleSheet(f"color: {colors.primary}; font-size: 16px; font-weight: 700; background: transparent;")
        input_layout.addWidget(prompt)

        self._input = QLineEdit()
        self._input.setPlaceholderText(placeholder)
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background: transparent;
                border: none;
                color: {colors.text_primary};
                font-size: 15px;
                font-weight: 500;
            }}
            QLineEdit::placeholder {{
                color: {colors.text_disabled};
            }}
        """)
        self._input.textChanged.connect(self._filter_commands)
        self._input.returnPressed.connect(self._on_submit)
        input_layout.addWidget(self._input, 1)

        layout.addWidget(input_frame)

        self._list = QListWidget()
        self._list.setStyleSheet(f"""
            QListWidget {{
                background: transparent;
                border: none;
                border-top: 1px solid {colors.border};
                color: {colors.text_primary};
                font-size: 13px;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 8px 16px;
                border-radius: {RADIUS.sm};
            }}
            QListWidget::item:hover {{
                background-color: {colors.surface_hover};
            }}
            QListWidget::item:selected {{
                background-color: {colors.primary_variant};
                color: {colors.primary};
            }}
        """)
        self._list.itemClicked.connect(lambda item: self.command_selected.emit(item.data(Qt.UserRole)))
        self._list.setVisible(False)
        layout.addWidget(self._list)

    def _filter_commands(self, text: str) -> None:
        self._list.clear()
        if not text:
            self._list.setVisible(False)
            return

        filtered = [(cid, clabel) for cid, clabel in self._commands if text.lower() in clabel.lower()]
        if not filtered:
            self._list.setVisible(False)
            return

        for cid, clabel in filtered:
            item = QListWidgetItem(clabel)
            item.setData(Qt.UserRole, cid)
            self._list.addItem(item)

        self._list.setVisible(True)

    def _on_submit(self) -> None:
        text = self._input.text().strip()
        if text:
            self.command_selected.emit(text)
            self.hide()

    def show_command_bar(self) -> None:
        self._input.clear()
        self._list.setVisible(False)
        self.show()
        self._input.setFocus()
        self.raise_()

    def hide_command_bar(self) -> None:
        self.hide()
        self.dismissed.emit()

    def keyPressEvent(self, event) -> None:  # noqa: N802
        if event.matches(QKeySequence(Qt.Key_Escape)):
            self.hide_command_bar()
        super().keyPressEvent(event)
