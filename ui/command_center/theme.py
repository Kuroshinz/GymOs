from __future__ import annotations

from ui.design_system.tokens.color import (
    ColorScheme,
    DarkColorTokens,
    HighContrastColorTokens,
    color_from_scheme,
)
from ui.design_system.tokens.radius import RadiusTokens
from ui.design_system.tokens.spacing import SpacingTokens
from ui.design_system.tokens.typography import TypographyTokens


class C:
    _scheme = ColorScheme.DARK
    _hc = False

    @classmethod
    def _c(cls):
        if cls._hc:
            return HighContrastColorTokens()
        return color_from_scheme(cls._scheme)

    @classmethod
    def set_scheme(cls, scheme: ColorScheme, high_contrast: bool = False):
        cls._scheme = scheme
        cls._hc = high_contrast

    BG: str = DarkColorTokens.background
    CARD_BG: str = DarkColorTokens.surface
    CARD_HOVER: str = DarkColorTokens.surface_hover
    BORDER: str = DarkColorTokens.border
    BORDER_HOVER: str = DarkColorTokens.border_hover
    ACCENT: str = DarkColorTokens.primary
    ACCENT_HOVER: str = DarkColorTokens.primary_hover
    TEXT_PRIMARY: str = DarkColorTokens.text_primary
    TEXT_SECONDARY: str = DarkColorTokens.text_secondary
    TEXT_MUTED: str = DarkColorTokens.text_disabled
    TEXT_DANGER: str = DarkColorTokens.error
    TEXT_WARN: str = DarkColorTokens.warning
    TEXT_SUCCESS: str = DarkColorTokens.success
    TEXT_INFO: str = DarkColorTokens.secondary
    SIDEBAR_BG: str = DarkColorTokens.background_alt
    SIDEBAR_HOVER: str = DarkColorTokens.surface
    SIDEBAR_ACTIVE: str = DarkColorTokens.surface
    SCROLLBAR_BG: str = DarkColorTokens.background
    SCROLLBAR_HANDLE: str = DarkColorTokens.scrollbar_handle
    SCROLLBAR_HOVER: str = DarkColorTokens.scrollbar_hover


_c = DarkColorTokens()
S = SpacingTokens()
R = RadiusTokens()
T = TypographyTokens()


class Font:
    HEADING = f"color: {_c.text_primary}; font-size: 28px; font-weight: 700;"
    SUBHEADING = f"color: {_c.text_primary}; font-size: 18px; font-weight: 600;"
    TITLE = f"color: {_c.text_primary}; font-size: 15px; font-weight: 600;"
    BODY = f"color: {_c.text_secondary}; font-size: 13px;"
    MUTED = f"color: {_c.text_disabled}; font-size: 13px;"
    LABEL = f"color: {_c.text_secondary}; font-size: 11px; font-weight: 600; letter-spacing: 0.5px; text-transform: uppercase;"
    CAPTION = f"color: {_c.text_disabled}; font-size: 11px;"
    STAT_VALUE = f"color: {_c.text_primary}; font-size: 20px; font-weight: 700;"
    STAT_LABEL = f"color: {_c.text_disabled}; font-size: 12px; font-weight: 500;"
    BADGE = f"background-color: {_c.border}; color: {_c.text_secondary}; border-radius: 8px; padding: 2px 8px; font-size: 11px;"


class Style:
    CARD = f"""
        CommandCenterCard {{
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(18, 19, 36, 0.85),
                stop:1 rgba(10, 11, 22, 0.85)); /* {_c.surface} */
            border-radius: 12px;
            border: 1px solid rgba(99, 102, 241, 0.15); /* {_c.border} */
        }}
        CommandCenterCard:hover {{
            border-color: rgba(99, 102, 241, 0.35);
        }}
    """
    WIDGET = CARD_BASE = f"""
        QWidget {{
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(18, 19, 36, 0.85),
                stop:1 rgba(10, 11, 22, 0.85)); /* {_c.surface} */
            border-radius: 12px;
            border: 1px solid rgba(99, 102, 241, 0.15); /* {_c.border} */
        }}
    """
    SCROLL = f"""
        QScrollArea {{
            background-color: {_c.background};
            border: none;
        }}
        QScrollBar:vertical {{
            background-color: {_c.background};
            width: 8px;
            border: none;
        }}
        QScrollBar::handle:vertical {{
            background-color: {_c.scrollbar_handle};
            border-radius: 4px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background-color: {_c.scrollbar_hover};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
    """
    SIDEBAR = f"""
        QFrame#sidebar {{
            background-color: {_c.background_alt};
            border-right: 1px solid {_c.border};
        }}
    """


NAV_ITEMS = [
    ("home", "EXECUTIVE", "\U0001F3E0", "Recovery / Readiness / Insights / Activity"),
    ("intelligence", "BRIEFING", "\U0001F4AC", "Coach narratives / Insights / Decisions"),
    ("mission", "GOALS", "\U0001F9E0", "Intent / Progress / Timeline"),
    ("planning", "PLANNING", "\U0001F4CB", "Cycle / Volume / Sessions / Optimizer"),
    ("prediction", "FORECAST", "\U0001F52E", "Trends / Projections / Confidence"),
    ("recovery", "RECOVERY", "\U0001F9CD", "Score / Sleep / Stress / Fatigue"),
    ("knowledge", "KNOWLEDGE", "\U0001F4DA", "Graph / Insights / Updates / Patterns"),
    ("adaptive", "OPTIMIZE", "\U0001F4A1", "Adaptations / Decisions / Strategy"),
    ("analytics", "LAB", "\U0001F4CA", "Volume / Compliance / PRs / Trends"),
    ("system", "CONSOLE", "\u2699\uFE0F", "Health / Capabilities / Kernel / Release"),
]

PAGE_LABELS = {
    "home": "Executive Dashboard",
    "mission": "Goal Workspace",
    "planning": "Planning Studio",
    "prediction": "Forecast Studio",
    "recovery": "Recovery Center",
    "knowledge": "Knowledge Explorer",
    "adaptive": "Optimization Center",
    "analytics": "Performance Lab",
    "system": "Platform Console",
    "intelligence": "AI Briefing Center",
}
