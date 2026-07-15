from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ColorScheme(Enum):
    LIGHT = "light"
    DARK = "dark"
    HIGH_CONTRAST = "high_contrast"


@dataclass(frozen=True)
class ColorTokens:
    primary: str = "#6366F1"
    primary_hover: str = "#4F46E5"
    primary_variant: str = "#EEF2FF"

    secondary: str = "#38BDF8"
    secondary_hover: str = "#2BA0E8"
    secondary_variant: str = "#ECFEFF"

    accent: str = "#F9A03F"
    accent_hover: str = "#E88D2A"
    accent_variant: str = "#FFFBEB"

    success: str = "#34D399"
    success_hover: str = "#2BBF7D"
    success_surface: str = "#ECFDF5"
    success_border: str = "#A7F3D0"

    warning: str = "#F5A623"
    warning_hover: str = "#DF931A"
    warning_surface: str = "#FFFBEB"
    warning_border: str = "#FDE68A"

    error: str = "#F56565"
    error_hover: str = "#E53E3E"
    error_surface: str = "#FEF2F2"
    error_border: str = "#FECACA"

    info: str = "#3B82F6"
    info_hover: str = "#2563EB"
    info_surface: str = "#EFF6FF"
    info_border: str = "#BFDBFE"

    background: str = "#F7F8FA"
    background_alt: str = "#F0F2F5"
    surface: str = "#FFFFFF"
    surface_hover: str = "#FAFBFC"
    surface_active: str = "#F3F4F6"
    surface_raised: str = "#FAFBFC"
    surface_elevated: str = "#FFFFFF"
    border: str = "rgba(0, 0, 0, 0.06)"
    border_light: str = "rgba(0, 0, 0, 0.03)"
    border_hover: str = "rgba(0, 0, 0, 0.12)"

    text_primary: str = "#0F172A"
    text_secondary: str = "#6B7280"
    text_disabled: str = "#9CA3AF"
    text_inverse: str = "#FFFFFF"
    text_link: str = "#4F46E5"

    overlay: str = "rgba(0, 0, 0, 0.4)"
    focus_ring: str = "rgba(99, 102, 241, 0.4)"
    scrollbar_bg: str = "transparent"
    scrollbar_handle: str = "#D1D5DB"
    scrollbar_hover: str = "#9CA3AF"


@dataclass(frozen=True)
class DarkColorTokens:
    primary: str = "#6366F1"
    primary_hover: str = "#818CF8"
    primary_variant: str = "#1E1B4B"

    secondary: str = "#38BDF8"
    secondary_hover: str = "#0EA5E9"
    secondary_variant: str = "#082F49"

    accent: str = "#D946EF"
    accent_hover: str = "#F43F5E"
    accent_variant: str = "#4C0519"

    success: str = "#34D399"
    success_hover: str = "#2BBF7D"
    success_surface: str = "#0A2A1A"
    success_border: str = "#1A4538"

    warning: str = "#FBBF24"
    warning_hover: str = "#F59E0B"
    warning_surface: str = "#2E1C0C"
    warning_border: str = "#4D3018"

    error: str = "#FB7185"
    error_hover: str = "#F43F5E"
    error_surface: str = "#2D0F0F"
    error_border: str = "#4F1D1D"

    info: str = "#60A5FA"
    info_hover: str = "#3B82F6"
    info_surface: str = "#0F1D40"
    info_border: str = "#1A3060"

    background: str = "#070814"
    background_alt: str = "#0B0C1E"
    surface: str = "#121324"
    surface_hover: str = "#181932"
    surface_active: str = "#202144"
    surface_raised: str = "#181932"
    surface_elevated: str = "#15162D"
    border: str = "rgba(99, 102, 241, 0.12)"
    border_light: str = "rgba(99, 102, 241, 0.06)"
    border_hover: str = "rgba(99, 102, 241, 0.25)"

    text_primary: str = "#F8FAFC"
    text_secondary: str = "#94A3B8"
    text_disabled: str = "#475569"
    text_inverse: str = "#FFFFFF"
    text_link: str = "#818CF8"

    overlay: str = "rgba(0, 0, 0, 0.6)"
    focus_ring: str = "rgba(99, 102, 241, 0.5)"
    scrollbar_bg: str = "transparent"
    scrollbar_handle: str = "rgba(99, 102, 241, 0.25)"
    scrollbar_hover: str = "rgba(99, 102, 241, 0.4)"


@dataclass(frozen=True)
class HighContrastColorTokens:
    primary: str = "#4F46E5"
    primary_hover: str = "#4338CA"
    primary_variant: str = "#EEF2FF"

    secondary: str = "#0891B2"
    secondary_hover: str = "#0E7490"
    secondary_variant: str = "#ECFEFF"

    accent: str = "#D97706"
    accent_hover: str = "#B45309"
    accent_variant: str = "#FFFBEB"

    success: str = "#16A34A"
    success_hover: str = "#15803D"
    success_surface: str = "#F0FDF4"
    success_border: str = "#86EFAC"

    warning: str = "#CA8A04"
    warning_hover: str = "#A16207"
    warning_surface: str = "#FEFCE8"
    warning_border: str = "#FDE047"

    error: str = "#DC2626"
    error_hover: str = "#B91C1C"
    error_surface: str = "#FEF2F2"
    error_border: str = "#FCA5A5"

    info: str = "#2563EB"
    info_hover: str = "#1D4ED8"
    info_surface: str = "#EFF6FF"
    info_border: str = "#93C5FD"

    background: str = "#FFFFFF"
    background_alt: str = "#F8FAFC"
    surface: str = "#E2E8F0"
    surface_hover: str = "#CBD5E1"
    surface_active: str = "#94A3B8"
    surface_raised: str = "#CBD5E1"
    surface_elevated: str = "#E2E8F0"
    border: str = "#64748B"
    border_light: str = "#94A3B8"
    border_hover: str = "#475569"

    text_primary: str = "#000000"
    text_secondary: str = "#1E293B"
    text_disabled: str = "#64748B"
    text_inverse: str = "#FFFFFF"
    text_link: str = "#4338CA"

    overlay: str = "rgba(0, 0, 0, 0.5)"
    focus_ring: str = "rgba(79, 70, 229, 0.6)"
    scrollbar_bg: str = "transparent"
    scrollbar_handle: str = "#94A3B8"
    scrollbar_hover: str = "#64748B"


@dataclass(frozen=True)
class SemanticColorTokens:
    danger: str = "#F56565"
    danger_hover: str = "#E53E3E"
    danger_surface: str = "#FEF2F2"
    danger_border: str = "#FECACA"

    warning: str = "#F5A623"
    warning_hover: str = "#DF931A"
    warning_surface: str = "#FFFBEB"
    warning_border: str = "#FDE68A"

    success: str = "#34D399"
    success_hover: str = "#2BBF7D"
    success_surface: str = "#ECFDF5"
    success_border: str = "#A7F3D0"

    info: str = "#6366F1"
    info_hover: str = "#4F46E5"
    info_surface: str = "#EEF2FF"
    info_border: str = "#C7D2FE"

    neutral: str = "#6B7280"
    neutral_hover: str = "#4B5563"
    neutral_surface: str = "#F9FAFB"
    neutral_border: str = "#E5E7EB"


_SCHEME_MAP: dict[ColorScheme, type[ColorTokens | DarkColorTokens | HighContrastColorTokens]] = {
    ColorScheme.LIGHT: ColorTokens,
    ColorScheme.DARK: DarkColorTokens,
    ColorScheme.HIGH_CONTRAST: HighContrastColorTokens,
}


def color_from_scheme(
    scheme: ColorScheme,
) -> ColorTokens | DarkColorTokens | HighContrastColorTokens:
    cls = _SCHEME_MAP.get(scheme)
    if cls is None:
        return ColorTokens()
    return cls()


def resolve_alpha(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"
