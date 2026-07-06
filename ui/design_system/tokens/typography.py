from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TypographyTokens:
    font_family: str = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    font_family_mono: str = "JetBrains Mono, Fira Code, monospace"
    font_family_display: str = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"

    h1_size: str = "2.25rem"
    h1_weight: str = "700"
    h1_line_height: str = "1.25"
    h1_letter_spacing: str = "-0.025em"

    h2_size: str = "1.875rem"
    h2_weight: str = "700"
    h2_line_height: str = "1.3"
    h2_letter_spacing: str = "-0.02em"

    h3_size: str = "1.5rem"
    h3_weight: str = "600"
    h3_line_height: str = "1.35"
    h3_letter_spacing: str = "-0.015em"

    h4_size: str = "1.25rem"
    h4_weight: str = "600"
    h4_line_height: str = "1.4"
    h4_letter_spacing: str = "-0.01em"

    body_size: str = "1rem"
    body_weight: str = "400"
    body_line_height: str = "1.5"
    body_letter_spacing: str = "0em"

    body_small_size: str = "0.875rem"
    body_small_weight: str = "400"
    body_small_line_height: str = "1.5"
    body_small_letter_spacing: str = "0em"

    caption_size: str = "0.75rem"
    caption_weight: str = "400"
    caption_line_height: str = "1.5"
    caption_letter_spacing: str = "0.025em"

    label_size: str = "0.75rem"
    label_weight: str = "600"
    label_line_height: str = "1.25"
    label_letter_spacing: str = "0.05em"

    overline_size: str = "0.625rem"
    overline_weight: str = "700"
    overline_line_height: str = "1.25"
    overline_letter_spacing: str = "0.075em"

    weight_thin: str = "100"
    weight_light: str = "300"
    weight_normal: str = "400"
    weight_medium: str = "500"
    weight_semibold: str = "600"
    weight_bold: str = "700"
    weight_extrabold: str = "800"

    line_height_tight: str = "1.25"
    line_height_normal: str = "1.5"
    line_height_relaxed: str = "1.75"


@dataclass(frozen=True)
class type_scale:
    xs: str = "0.75rem"
    sm: str = "0.875rem"
    base: str = "1rem"
    lg: str = "1.125rem"
    xl: str = "1.25rem"
    size_2xl: str = "1.5rem"
    size_3xl: str = "1.875rem"
    size_4xl: str = "2.25rem"
    size_5xl: str = "3rem"


_STYLE_TEMPLATE = "font-family: {family}; font-size: {size}; font-weight: {weight}; line-height: {lheight}; letter-spacing: {lspace};"
_WEIGHT_MAP = {
    "thin": "100",
    "light": "300",
    "normal": "400",
    "medium": "500",
    "semibold": "600",
    "bold": "700",
    "extrabold": "800",
}


def font_style(
    size: str = "body",
    weight: str | int = "normal",
    family: str = "font_family",
    line_height: str | None = None,
) -> str:
    tok = TypographyTokens()
    size_key = f"{size}_size" if not size.endswith("_size") else size
    weight_str = str(weight)
    weight_key = f"{size}_weight" if not weight_str.endswith("_weight") else weight_str
    lh_key = f"{size}_line_height" if line_height is None else None

    resolved_size = getattr(tok, size_key, tok.body_size)
    resolved_weight = _WEIGHT_MAP.get(weight_str, getattr(tok, weight_key, tok.weight_normal))
    resolved_family = getattr(tok, family, tok.font_family)
    resolved_lh = getattr(tok, lh_key, tok.line_height_normal) if lh_key else line_height

    return _STYLE_TEMPLATE.format(
        family=resolved_family,
        size=resolved_size,
        weight=resolved_weight,
        lheight=resolved_lh,
        lspace=getattr(tok, f"{size}_letter_spacing", "0em"),
    )
