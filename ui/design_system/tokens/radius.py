from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RadiusTokens:
    none: str = "0px"
    sm: str = "0.375rem"
    md: str = "0.625rem"
    lg: str = "1rem"
    xl: str = "1.25rem"
    size_2xl: str = "1.75rem"
    full: str = "9999px"


@dataclass(frozen=True)
class BorderTokens:
    none: str = "none"
    thin: str = "1px solid"
    normal: str = "1px solid"
    medium: str = "2px solid"
    thick: str = "3px solid"


_BASE_FONT_SIZE = 16


def radius_to_px(radius_str: str) -> int:
    if radius_str.endswith("px"):
        return int(radius_str.replace("px", ""))
    if radius_str.endswith("rem"):
        return int(float(radius_str.replace("rem", "")) * _BASE_FONT_SIZE)
    return 0


def px_from_token(token_str: str) -> int:
    if token_str.endswith("px"):
        return int(token_str.replace("px", ""))
    if token_str.endswith("rem"):
        return int(float(token_str.replace("rem", "")) * _BASE_FONT_SIZE)
    return 0
