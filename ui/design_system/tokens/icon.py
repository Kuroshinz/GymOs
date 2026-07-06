from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class IconTokens:
    xs: str = "12px"
    sm: str = "14px"
    md: str = "16px"
    lg: str = "20px"
    xl: str = "24px"
    size_2xl: str = "32px"
    size_3xl: str = "40px"
    size_4xl: str = "48px"

    icon_button: str = "20px"
    menu_icon: str = "16px"
    badge_icon: str = "12px"
    decorative: str = "24px"
    avatar: str = "32px"
