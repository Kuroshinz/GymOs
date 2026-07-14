from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ColorTokens:
    primary: str = "#6366F1"
    primary_hover: str = "#4F46E5"
    secondary: str = "#06B6D4"
    accent: str = "#F59E0B"
    success: str = "#22C55E"
    warning: str = "#EAB308"
    error: str = "#EF4444"
    info: str = "#3B82F6"

    background: str = "#FFFFFF"
    surface: str = "#F9FAFB"
    surface_hover: str = "#F3F4F6"
    border: str = "#E5E7EB"

    text_primary: str = "#111827"
    text_secondary: str = "#6B7280"
    text_disabled: str = "#9CA3AF"
    text_inverse: str = "#FFFFFF"


@dataclass(frozen=True)
class DarkColorTokens:
    primary: str = "#818CF8"
    primary_hover: str = "#6366F1"
    secondary: str = "#22D3EE"
    accent: str = "#FBBF24"
    success: str = "#4ADE80"
    warning: str = "#FACC15"
    error: str = "#F87171"
    info: str = "#60A5FA"

    background: str = "#0F172A"
    surface: str = "#1E293B"
    surface_hover: str = "#334155"
    border: str = "#475569"

    text_primary: str = "#F1F5F9"
    text_secondary: str = "#94A3B8"
    text_disabled: str = "#64748B"
    text_inverse: str = "#0F172A"


@dataclass(frozen=True)
class TypographyTokens:
    font_family: str = "Inter, -apple-system, BlinkMacSystemFont, sans-serif"
    font_family_mono: str = "JetBrains Mono, Fira Code, monospace"

    h1: str = "2.25rem"
    h2: str = "1.875rem"
    h3: str = "1.5rem"
    h4: str = "1.25rem"
    body: str = "1rem"
    body_small: str = "0.875rem"
    caption: str = "0.75rem"

    weight_normal: str = "400"
    weight_medium: str = "500"
    weight_semibold: str = "600"
    weight_bold: str = "700"

    line_height_tight: str = "1.25"
    line_height_normal: str = "1.5"
    line_height_relaxed: str = "1.75"


@dataclass(frozen=True)
class SpacingTokens:
    xs: str = "0.25rem"
    sm: str = "0.5rem"
    md: str = "1rem"
    lg: str = "1.5rem"
    xl: str = "2rem"
    xxl: str = "3rem"

    section: str = "1.5rem"
    page: str = "2rem"


@dataclass(frozen=True)
class BorderRadiusTokens:
    sm: str = "0.25rem"
    md: str = "0.5rem"
    lg: str = "0.75rem"
    xl: str = "1rem"
    full: str = "9999px"


@dataclass(frozen=True)
class ShadowTokens:
    sm: str = "0 1px 2px 0 rgb(0 0 0 / 0.05)"
    md: str = "0 4px 6px -1px rgb(0 0 0 / 0.1)"
    lg: str = "0 10px 15px -3px rgb(0 0 0 / 0.1)"
    xl: str = "0 20px 25px -5px rgb(0 0 0 / 0.1)"


@dataclass
class Theme:
    name: str
    colors: ColorTokens
    dark_colors: ColorTokens | None = None
    typography: TypographyTokens = field(default_factory=TypographyTokens)
    spacing: SpacingTokens = field(default_factory=SpacingTokens)
    radius: BorderRadiusTokens = field(default_factory=BorderRadiusTokens)
    shadows: ShadowTokens = field(default_factory=ShadowTokens)
    is_dark: bool = False

    @property
    def current_colors(self) -> ColorTokens:
        if self.is_dark and self.dark_colors:
            return self.dark_colors
        return self.colors


LIGHT_THEME = Theme(
    name="light",
    colors=ColorTokens(),
    dark_colors=DarkColorTokens(),
    typography=TypographyTokens(),
    spacing=SpacingTokens(),
    radius=BorderRadiusTokens(),
    shadows=ShadowTokens(),
)

DARK_THEME = Theme(
    name="dark",
    colors=ColorTokens(),
    dark_colors=DarkColorTokens(),
    typography=TypographyTokens(),
    spacing=SpacingTokens(),
    radius=BorderRadiusTokens(),
    shadows=ShadowTokens(),
    is_dark=True,
)


class ThemeManager:
    _instance: ThemeManager | None = None

    def __new__(cls) -> ThemeManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._themes: dict[str, Theme] = {}
            cls._instance._current: Theme | None = None
        return cls._instance

    def __init__(self) -> None:
        if not self._themes:
            self.register(LIGHT_THEME)
            self.register(DARK_THEME)
            self._current = LIGHT_THEME

    def register(self, theme: Theme) -> None:
        self._themes[theme.name] = theme

    def activate(self, name: str) -> None:
        if name not in self._themes:
            raise KeyError(f"Theme '{name}' not found. Available: {list(self._themes.keys())}")
        self._current = self._themes[name]

    def toggle_dark_mode(self) -> None:
        if self._current:
            self._current.is_dark = not self._current.is_dark

    @property
    def current(self) -> Theme:
        if self._current is None:
            self._current = LIGHT_THEME
        return self._current

    @property
    def available_themes(self) -> list[str]:
        return list(self._themes.keys())
