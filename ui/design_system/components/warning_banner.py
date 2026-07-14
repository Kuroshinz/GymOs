from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens
from ui.design_system.tokens.typography import font_style

R = RadiusTokens()


class WarningBanner(QFrame):
    action_clicked = Signal()

    def __init__(
        self,
        icon: str = "",
        message: str = "",
        action_text: str = "",
        level: str = "warning",
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._level = level
        self.setAccessibleName(f"Banner: {message}"[:64] if message else "Warning banner")
        self._build_ui(icon, message, action_text)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _build_ui(self, icon: str, message: str, action_text: str) -> None:
        colors = self._colors()

        if self._level == "error":
            bg = colors.error_surface
            border = colors.error_border
            text_c = colors.error
        elif self._level == "success":
            bg = colors.success_surface
            border = colors.success_border
            text_c = colors.success
        else:
            bg = colors.warning_surface
            border = colors.warning_border
            text_c = colors.warning

        self.setStyleSheet(f"""
            WarningBanner {{
                background-color: {bg};
                border-radius: {R.md};
                border: 1px solid {border};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(10)

        if icon:
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 16px; background: transparent; border: none;")
            layout.addWidget(icon_lbl)

        msg = QLabel(message)
        msg.setStyleSheet(
            f"color: {text_c}; {font_style('body', weight=500)}; "
            f"background: transparent; border: none;"
        )
        msg.setWordWrap(True)
        layout.addWidget(msg, 1)

        if action_text:
            btn = QPushButton(action_text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    color: {text_c};
                    background-color: transparent;
                    border: 1px solid {border};
                    border-radius: 4px;
                    padding: 4px 12px;
                    font-size: 12px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {border};
                }}
            """)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(self.action_clicked.emit)
            layout.addWidget(btn)
