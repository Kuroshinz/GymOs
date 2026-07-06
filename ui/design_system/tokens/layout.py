from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class LayoutBreakpoint(Enum):
    XS = 0
    SM = 640
    MD = 768
    LG = 1024
    XL = 1280
    XL2 = 1536


_BREAKPOINT_MAP: dict[str, int] = {
    "xs": 0,
    "sm": 640,
    "md": 768,
    "lg": 1024,
    "xl": 1280,
    "xl2": 1536,
}


def breakpoint(name: str) -> int:
    return _BREAKPOINT_MAP.get(name, 0)


@dataclass(frozen=True)
class LayoutTokens:
    max_width_xs: str = "320px"
    max_width_sm: str = "640px"
    max_width_md: str = "768px"
    max_width_lg: str = "1024px"
    max_width_xl: str = "1280px"
    max_width_xl2: str = "1536px"
    max_width_full: str = "100%"

    container_padding_xs: str = "0.5rem"
    container_padding_sm: str = "1rem"
    container_padding_md: str = "1.5rem"
    container_padding_lg: str = "2rem"
    container_padding_xl: str = "2rem"

    columns_1: str = "1fr"
    columns_2: str = "1fr 1fr"
    columns_3: str = "1fr 1fr 1fr"
    columns_4: str = "1fr 1fr 1fr 1fr"
    columns_auto_fill: str = "repeat(auto-fill, minmax(300px, 1fr))"
    columns_auto_fit: str = "repeat(auto-fit, minmax(280px, 1fr))"

    sidebar_width: str = "240px"
    sidebar_collapsed: str = "56px"
    navigation_rail_width: str = "72px"
    toolbar_height: str = "48px"
    command_bar_height: str = "44px"
    section_gap: str = "1.5rem"
    content_gap: str = "1rem"
    page_margin: str = "1.5rem"
