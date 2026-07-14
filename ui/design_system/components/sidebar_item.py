from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens

RADIUS = RadiusTokens()


class SidebarItem(QPushButton):
    def __init__(
        self,
        text: str = "",
        icon: str = "",
        active: bool = False,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._active = active
        self._color_scheme = color_scheme
        icon_text = f"{icon} " if icon else ""
        self.setText(f"{icon_text}{text}")
        self.setFixedHeight(44)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.StrongFocus)
        if text:
            self.setAccessibleName(f"Navigate to {text}")
        if tooltip := (icon_text + text if icon_text else text):
            self.setToolTip(tooltip)
        self._update_style()

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _update_style(self) -> None:
        colors = self._colors()
        bg = colors.primary_variant if self._active else "transparent"
        color = colors.primary if self._active else colors.text_secondary
        weight = "600" if self._active else "500"
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {color};
                border: 1px solid transparent;
                border-radius: {RADIUS.md};
                padding: 8px 16px;
                text-align: left;
                font-size: 13px;
                font-weight: {weight};
            }}
            QPushButton:hover {{
                background-color: {colors.surface_hover};
                color: {colors.text_primary};
            }}
            QPushButton:focus {{
                border-color: {colors.focus_ring};
            }}
        """)

    def set_active(self, active: bool) -> None:
        if active != self._active:
            self._active = active
            self._update_style()
