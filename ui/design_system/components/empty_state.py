from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.spacing import SpacingTokens

SPACE = SpacingTokens()


class EmptyState(QFrame):
    def __init__(
        self,
        icon: str = "\U0001F4E6",
        title: str = "No data",
        message: str = "Nothing to display yet.",
        action_text: str = "",
        on_action: Callable[[], None] | None = None,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._build_ui(icon, title, message, action_text, on_action)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _build_ui(
        self,
        icon: str,
        title: str,
        message: str,
        action_text: str,
        on_action: Callable | None,
    ) -> None:
        colors = self._colors()
        self.setStyleSheet(
            "EmptyState { background: transparent; border: none; }"
        )

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet(
            "font-size: 48px; background: transparent; border: none;"
        )
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 16px; font-weight: 600; "
            f"background: transparent; border: none;"
        )
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        msg_label = QLabel(message)
        msg_label.setStyleSheet(
            f"color: {colors.text_secondary}; font-size: 13px; "
            f"background: transparent; border: none;"
        )
        msg_label.setAlignment(Qt.AlignCenter)
        msg_label.setWordWrap(True)
        layout.addWidget(msg_label)

        if action_text:
            btn = QPushButton(action_text)
            btn.setAccessibleName(action_text)
            btn.setToolTip(action_text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors.primary};
                    color: {colors.text_inverse};
                    border: 1px solid transparent;
                    border-radius: 6px;
                    padding: 8px 20px;
                    font-size: 13px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {colors.primary_hover};
                }}
                QPushButton:focus {{
                    border-color: {colors.focus_ring};
                }}
            """)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
            if on_action:
                btn.clicked.connect(on_action)
            layout.addWidget(btn, 0, Qt.AlignCenter)

    def set_message(self, title: str, message: str) -> None:
        pass
