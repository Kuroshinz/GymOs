from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SpacingTokens:
    px: str = "1px"
    half: str = "0.125rem"
    s1: str = "0.25rem"
    s1_5: str = "0.375rem"
    s2: str = "0.5rem"
    s2_5: str = "0.625rem"
    s3: str = "0.75rem"
    s3_5: str = "0.875rem"
    s4: str = "1rem"
    s5: str = "1.25rem"
    s6: str = "1.5rem"
    s7: str = "1.75rem"
    s8: str = "2rem"
    s9: str = "2.25rem"
    s10: str = "2.5rem"
    s11: str = "2.75rem"
    s12: str = "3rem"
    s14: str = "3.5rem"
    s16: str = "4rem"
    s20: str = "5rem"
    s24: str = "6rem"
    s28: str = "7rem"
    s32: str = "8rem"
    s36: str = "9rem"
    s40: str = "10rem"
    s44: str = "11rem"
    s48: str = "12rem"
    s52: str = "13rem"
    s56: str = "14rem"
    s60: str = "15rem"
    s64: str = "16rem"

    page_margin: str = "2.5rem"
    section_gap: str = "2rem"
    card_gap: str = "1.25rem"
    card_padding: str = "1.5rem"
    dense_padding: str = "1.25rem"
    row_gap: str = "0.75rem"
    item_gap: str = "0.5rem"
    inline_gap: str = "0.25rem"
    hero_gap: str = "2rem"
    content_gap: str = "1rem"

    # Deprecated aliases — kept for backward compatibility
    section: str = "1.5rem"
    page: str = "2rem"
    gutter: str = "1.5rem"
    container_padding: str = "1rem"
    list_gap: str = "0.5rem"

    _MULTIPLIER: float = 0.25

    def step(self, n: int) -> str:
        value = n * self._MULTIPLIER
        if value == int(value):
            return f"{int(value)}rem"
        return f"{value}rem"


def spacing_step(n: int) -> str:
    return SpacingTokens().step(n)
