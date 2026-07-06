from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.layout import LayoutTokens
from ui.design_system.tokens.radius import RadiusTokens, px_from_token
from ui.design_system.tokens.spacing import SpacingTokens

RADIUS = RadiusTokens()
SPACE = SpacingTokens()
LAYOUT = LayoutTokens()


@dataclass
class NavigationItem:
    id: str
    label: str
    icon: str = ""
    tooltip: str = ""


class NavigationRail(QFrame):
    item_selected = Signal(str)

    def __init__(
        self,
        items: Sequence[NavigationItem] | None = None,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._items: dict[str, NavigationItem] = {}
        self._buttons: dict[str, QPushButton] = {}
        self._active_id: str = ""
        self._build_ui(items or [])

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _build_ui(self, items: Sequence[NavigationItem]) -> None:
        colors = self._colors()
        self.setFixedWidth(px_from_token(LAYOUT.navigation_rail_width))
        self.setStyleSheet(f"""
            NavigationRail {{
                background-color: {colors.background_alt};
                border-right: 1px solid {colors.border};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 16, 0, 16)
        layout.setSpacing(2)

        logo = QLabel("N")
        logo.setStyleSheet(
            f"color: {colors.primary}; font-size: 22px; font-weight: 800; "
            f"background: transparent; border: none; padding: 8px 0;"
        )
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)
        layout.addSpacing(16)

        for item in items:
            btn = self._make_button(item)
            self._buttons[item.id] = btn
            self._items[item.id] = item
            layout.addWidget(btn)

        layout.addStretch()

        if self._buttons:
            first_id = next(iter(self._buttons))
            self._set_active(first_id)

    def _make_button(self, item: NavigationItem) -> QPushButton:
        colors = self._colors()
        btn = QPushButton()
        text = f"{item.icon} " if item.icon else ""
        btn.setText(f"{text}{item.label[0] if len(item.label) > 0 else ''}")
        btn.setToolTip(item.tooltip or item.label)
        btn.setFixedHeight(48)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda: self._on_item_clicked(item.id))
        return btn

    def _on_item_clicked(self, item_id: str) -> None:
        self._set_active(item_id)
        self.item_selected.emit(item_id)

    def _set_active(self, item_id: str) -> None:
        colors = self._colors()
        for pid, btn in self._buttons.items():
            active = pid == item_id
            bg = colors.primary_variant if active else "transparent"
            text_color = colors.primary if active else colors.text_secondary
            weight = "600" if active else "500"
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {bg};
                    color: {text_color};
                    border: none;
                    border-radius: {RADIUS.md};
                    padding: 8px 0;
                    font-size: 13px;
                    font-weight: {weight};
                }}
                QPushButton:hover {{
                    background-color: {colors.surface_hover if not active else colors.primary_variant};
                    color: {colors.text_primary if not active else colors.primary};
                }}
            """)
        self._active_id = item_id

    def set_active(self, item_id: str) -> None:
        if item_id in self._buttons:
            self._set_active(item_id)

    def add_item(self, item: NavigationItem) -> None:
        self._items[item.id] = item
        btn = self._make_button(item)
        self._buttons[item.id] = btn

    def remove_item(self, item_id: str) -> None:
        if item_id in self._buttons:
            self._buttons[item_id].deleteLater()
            del self._buttons[item_id]
            del self._items[item_id]
