from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect, QWidget


@dataclass(frozen=True)
class GlowTokens:
    primary: str = "rgba(124, 58, 237, 0.35)"
    goal: str = "rgba(251, 191, 36, 0.2)"
    success: str = "rgba(52, 211, 153, 0.25)"
    pr: str = "rgba(192, 132, 252, 0.3)"
    warning: str = "rgba(251, 191, 36, 0.15)"
    focus: str = "rgba(124, 58, 237, 0.5)"


_SHADOW_PARAMS: dict[int, tuple[int, int, int, float]] = {
    0: (0, 0, 0, 0.0),
    1: (0, 1, 4, 0.12),
    2: (0, 2, 8, 0.15),
    3: (0, 4, 16, 0.2),
    4: (0, 8, 24, 0.25),
    5: (0, 12, 32, 0.3),
}

_DARK_SHADOW_PARAMS: dict[int, tuple[int, int, int, float]] = {
    0: (0, 0, 0, 0.0),
    1: (0, 1, 6, 0.05),
    2: (0, 2, 12, 0.08),
    3: (0, 4, 20, 0.10),
    4: (0, 8, 32, 0.12),
    5: (0, 16, 48, 0.15),
}

_LIGHT_SHADOW_PARAMS: dict[int, tuple[int, int, int, float]] = {
    0: (0, 0, 0, 0.0),
    1: (0, 1, 4, 0.08),
    2: (0, 2, 8, 0.12),
    3: (0, 4, 16, 0.15),
    4: (0, 8, 24, 0.2),
    5: (0, 12, 32, 0.25),
}


def _parse_hex(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    if len(hex_color) == 6:
        return (int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))
    return (0, 0, 0)


def compute_shadow(
    bg_color: str,
    level: Literal[0, 1, 2, 3, 4, 5] = 1,
    is_dark: bool = True,
) -> str:
    params = _DARK_SHADOW_PARAMS if is_dark else _LIGHT_SHADOW_PARAMS
    dx, dy, blur, alpha = params.get(level, (0, 1, 4, 0.08))
    r, g, b = _parse_hex(bg_color)
    return f"{dx}px {dy}px {blur}px rgba({r},{g},{b},{alpha})"


def elevation_style(
    level: Literal[0, 1, 2, 3, 4, 5] = 0,
    is_dark: bool = False,
    bg_color: str | None = None,
) -> str:
    if level == 0:
        return "none"
    if bg_color:
        return compute_shadow(bg_color, level, is_dark)
    params = _DARK_SHADOW_PARAMS if is_dark else _LIGHT_SHADOW_PARAMS
    dx, dy, blur, alpha = params.get(level, (0, 1, 4, 0.08))
    return f"{dx}px {dy}px {blur}px rgba(0,0,0,{alpha})"


def apply_elevation(
    widget: QWidget,
    level: Literal[0, 1, 2, 3, 4, 5] = 0,
    is_dark: bool = False,
    bg_color: str = "#000000",
) -> None:
    if level == 0:
        widget.setGraphicsEffect(None)
        return
    params = _DARK_SHADOW_PARAMS if is_dark else _LIGHT_SHADOW_PARAMS
    dx, dy, blur, alpha = params.get(level, (0, 1, 4, 0.08))
    r, g, b = _parse_hex(bg_color)
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setOffset(dx, dy)
    shadow.setBlurRadius(blur)
    shadow.setColor(QColor(r, g, b, int(255 * alpha)))
    widget.setGraphicsEffect(shadow)


@dataclass(frozen=True)
class ElevationTokens:
    level_0: str = "none"
    level_1: str = "0 1px 4px 0 rgba(0, 0, 0, 0.08)"
    level_2: str = "0 2px 8px 0 rgba(0, 0, 0, 0.12)"
    level_3: str = "0 4px 16px 0 rgba(0, 0, 0, 0.15)"
    level_4: str = "0 8px 24px 0 rgba(0, 0, 0, 0.2)"
    level_5: str = "0 12px 32px 0 rgba(0, 0, 0, 0.25)"

    dark_level_0: str = "none"
    dark_level_1: str = "0 1px 4px 0 rgba(0, 0, 0, 0.08)"
    dark_level_2: str = "0 2px 8px 0 rgba(0, 0, 0, 0.12)"
    dark_level_3: str = "0 4px 16px 0 rgba(0, 0, 0, 0.15)"
    dark_level_4: str = "0 8px 24px 0 rgba(0, 0, 0, 0.2)"
    dark_level_5: str = "0 12px 32px 0 rgba(0, 0, 0, 0.25)"


def glow_effect(
    widget: QWidget,
    glow_rgba: str = "rgba(129, 140, 248, 0.25)",
    blur: int = 24,
    offset_y: int = 2,
) -> None:
    glow_rgba = glow_rgba.replace(" ", "")
    prefix = "rgba(" if glow_rgba.startswith("rgba(") else "rgba("
    inner = glow_rgba[len(prefix):-1]
    parts = inner.split(",")
    if len(parts) == 4:
        r, g, b, a = int(parts[0]), int(parts[1]), int(parts[2]), float(parts[3])
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setOffset(0, offset_y)
        shadow.setBlurRadius(blur)
        shadow.setColor(QColor(r, g, b, int(255 * a)))
        widget.setGraphicsEffect(shadow)
