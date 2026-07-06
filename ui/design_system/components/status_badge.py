from __future__ import annotations

from enum import Enum

from PySide6.QtWidgets import QLabel, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens

RADIUS = RadiusTokens()


class StatusLevel(Enum):
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"
    NEUTRAL = "neutral"


_LEVEL_COLORS = {
    StatusLevel.SUCCESS: ("success", "success_surface", "success_border"),
    StatusLevel.WARNING: ("warning", "warning_surface", "warning_border"),
    StatusLevel.ERROR: ("error", "error_surface", "error_border"),
    StatusLevel.INFO: ("info", "info_surface", "info_border"),
    StatusLevel.NEUTRAL: ("text_secondary", "surface", "border"),
}


class StatusBadge(QLabel):
    def __init__(
        self,
        text: str = "",
        level: StatusLevel = StatusLevel.NEUTRAL,
        outlined: bool = False,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._level = level
        self._outlined = outlined
        self._color_scheme = color_scheme
        self._update_style()

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _update_style(self) -> None:
        colors = self._colors()
        keys = _LEVEL_COLORS.get(self._level, _LEVEL_COLORS[StatusLevel.NEUTRAL])
        text_color = getattr(colors, keys[0])
        bg_color = "transparent" if self._outlined else getattr(colors, keys[1])
        border_color = getattr(colors, keys[2])

        border = f"1px solid {border_color}" if self._outlined else "none"
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: {text_color};
                border: {border};
                border-radius: {RADIUS.md};
                padding: 2px 8px;
                font-size: 11px;
                font-weight: 600;
            }}
        """)
        self.setFixedHeight(22)

    def set_level(self, level: StatusLevel) -> None:
        if level != self._level:
            self._level = level
            self._update_style()

    def set_text(self, text: str) -> None:
        self.setText(text)
