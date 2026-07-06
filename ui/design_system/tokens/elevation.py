from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget

_ELEVATION_SHADOWS = {
    0: "none",
    1: "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    2: "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)",
    3: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)",
    4: "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)",
    5: "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)",
}

_DARK_ELEVATION_SHADOWS = {
    0: "none",
    1: "0 1px 2px 0 rgba(0, 0, 0, 0.3)",
    2: "0 1px 3px 0 rgba(0, 0, 0, 0.4), 0 1px 2px -1px rgba(0, 0, 0, 0.3)",
    3: "0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -2px rgba(0, 0, 0, 0.3)",
    4: "0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -4px rgba(0, 0, 0, 0.3)",
    5: "0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.3)",
}

_SHADOW_PARAMS = {
    1: (0, 2, 8, 0.15),
    2: (0, 3, 12, 0.2),
    3: (0, 5, 16, 0.25),
    4: (0, 8, 24, 0.3),
    5: (0, 12, 32, 0.35),
}

_DARK_SHADOW_PARAMS = {
    1: (0, 2, 8, 0.3),
    2: (0, 3, 12, 0.4),
    3: (0, 5, 16, 0.45),
    4: (0, 8, 24, 0.5),
    5: (0, 12, 32, 0.55),
}


@dataclass(frozen=True)
class ElevationTokens:
    level_0: str = "none"
    level_1: str = "0 1px 2px 0 rgba(0, 0, 0, 0.05)"
    level_2: str = "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)"
    level_3: str = "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)"
    level_4: str = "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)"
    level_5: str = "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)"

    dark_level_0: str = "none"
    dark_level_1: str = "0 1px 2px 0 rgba(0, 0, 0, 0.3)"
    dark_level_2: str = "0 1px 3px 0 rgba(0, 0, 0, 0.4), 0 1px 2px -1px rgba(0, 0, 0, 0.3)"
    dark_level_3: str = "0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -2px rgba(0, 0, 0, 0.3)"
    dark_level_4: str = "0 10px 15px -3px rgba(0, 0, 0, 0.4), 0 4px 6px -4px rgba(0, 0, 0, 0.3)"
    dark_level_5: str = "0 20px 25px -5px rgba(0, 0, 0, 0.4), 0 8px 10px -6px rgba(0, 0, 0, 0.3)"


def elevation_style(level: Literal[0, 1, 2, 3, 4, 5] = 0, is_dark: bool = False) -> str:
    if is_dark:
        return _DARK_ELEVATION_SHADOWS.get(level, "none")
    return _ELEVATION_SHADOWS.get(level, "none")


def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def apply_elevation(
    widget: QWidget,
    level: Literal[0, 1, 2, 3, 4, 5] = 0,
    is_dark: bool = False,
    bg_color: str = "#000000",
) -> None:
    if level == 0:
        widget.setGraphicsEffect(None)
        return
    params = _DARK_SHADOW_PARAMS if is_dark else _SHADOW_PARAMS
    dx, dy, blur, alpha = params.get(level, (0, 2, 8, 0.2))
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setOffset(dx, dy)
    shadow.setBlurRadius(blur)
    from PySide6.QtGui import QColor
    r, g, b = int(bg_color[1:3], 16), int(bg_color[3:5], 16), int(bg_color[5:7], 16)
    shadow.setColor(QColor(r, g, b, int(255 * alpha)))
    widget.setGraphicsEffect(shadow)
