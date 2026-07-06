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

    secondary: str = "#06B6D4"
    secondary_hover: str = "#0891B2"
    secondary_variant: str = "#ECFEFF"

    accent: str = "#F59E0B"
    accent_hover: str = "#D97706"
    accent_variant: str = "#FFFBEB"

    success: str = "#22C55E"
    success_hover: str = "#16A34A"
    success_surface: str = "#F0FDF4"
    success_border: str = "#BBF7D0"

    warning: str = "#EAB308"
    warning_hover: str = "#CA8A04"
    warning_surface: str = "#FEFCE8"
    warning_border: str = "#FEF08A"

    error: str = "#EF4444"
    error_hover: str = "#DC2626"
    error_surface: str = "#FEF2F2"
    error_border: str = "#FECACA"

    info: str = "#3B82F6"
    info_hover: str = "#2563EB"
    info_surface: str = "#EFF6FF"
    info_border: str = "#BFDBFE"

    background: str = "#FFFFFF"
    background_alt: str = "#F8FAFC"
    surface: str = "#F9FAFB"
    surface_hover: str = "#F3F4F6"
    surface_active: str = "#E5E7EB"
    border: str = "#E5E7EB"
    border_light: str = "#F3F4F6"
    border_hover: str = "#D1D5DB"

    text_primary: str = "#111827"
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
    primary: str = "#818CF8"
    primary_hover: str = "#6366F1"
    primary_variant: str = "#1E1B4B"

    secondary: str = "#22D3EE"
    secondary_hover: str = "#06B6D4"
    secondary_variant: str = "#083344"

    accent: str = "#FBBF24"
    accent_hover: str = "#F59E0B"
    accent_variant: str = "#451A03"

    success: str = "#4ADE80"
    success_hover: str = "#22C55E"
    success_surface: str = "#052E16"
    success_border: str = "#166534"

    warning: str = "#FACC15"
    warning_hover: str = "#EAB308"
    warning_surface: str = "#422006"
    warning_border: str = "#713F12"

    error: str = "#F87171"
    error_hover: str = "#EF4444"
    error_surface: str = "#450A0A"
    error_border: str = "#7F1D1D"

    info: str = "#60A5FA"
    info_hover: str = "#3B82F6"
    info_surface: str = "#172554"
    info_border: str = "#1E40AF"

    background: str = "#0F172A"
    background_alt: str = "#0B1120"
    surface: str = "#1E293B"
    surface_hover: str = "#334155"
    surface_active: str = "#475569"
    border: str = "#334155"
    border_light: str = "#1E293B"
    border_hover: str = "#475569"

    text_primary: str = "#F1F5F9"
    text_secondary: str = "#94A3B8"
    text_disabled: str = "#64748B"
    text_inverse: str = "#0F172A"
    text_link: str = "#A5B4FC"

    overlay: str = "rgba(0, 0, 0, 0.6)"
    focus_ring: str = "rgba(129, 140, 248, 0.4)"
    scrollbar_bg: str = "transparent"
    scrollbar_handle: str = "#475569"
    scrollbar_hover: str = "#64748B"


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
    danger: str = "#EF4444"
    danger_hover: str = "#DC2626"
    danger_surface: str = "#FEF2F2"
    danger_border: str = "#FECACA"

    warning: str = "#F59E0B"
    warning_hover: str = "#D97706"
    warning_surface: str = "#FFFBEB"
    warning_border: str = "#FDE68A"

    success: str = "#10B981"
    success_hover: str = "#059669"
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
