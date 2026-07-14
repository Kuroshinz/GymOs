from __future__ import annotations

from collections.abc import Sequence

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens
from ui.design_system.tokens.spacing import SpacingTokens

SPACE = SpacingTokens()
RADIUS = RadiusTokens()


class Toolbar(QFrame):
    action_triggered = Signal(str)

    def __init__(
        self,
        title: str = "",
        actions: Sequence[tuple[str, str]] | None = None,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._build_ui(title, actions or [])

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _build_ui(self, title: str, actions: Sequence[tuple[str, str]]) -> None:
        colors = self._colors()
        self.setFixedHeight(48)
        self.setStyleSheet(f"""
            Toolbar {{
                background-color: {colors.background_alt};
                border-bottom: 1px solid {colors.border};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(8)

        if title:
            lbl = QLabel(title)
            lbl.setStyleSheet(
                f"color: {colors.text_primary}; font-size: 14px; font-weight: 600; "
                f"background: transparent; border: none;"
            )
            layout.addWidget(lbl)
            layout.addSpacing(8)

        layout.addStretch()

        for action_id, action_label in actions:
            btn = QPushButton(action_label)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {colors.text_secondary};
                    border: 1px solid transparent;
                    border-radius: {RADIUS.sm};
                    padding: 4px 12px;
                    font-size: 12px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    color: {colors.text_primary};
                    background-color: {colors.surface_hover};
                    border-color: {colors.border};
                }}
                QPushButton:pressed {{
                    background-color: {colors.surface_active};
                }}
            """)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked=False, aid=action_id: self.action_triggered.emit(aid))
            layout.addWidget(btn)

    def add_action(self, action_id: str, label: str) -> None:
        colors = self._colors()
        btn = QPushButton(label)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {colors.text_secondary};
                border: 1px solid transparent;
                border-radius: {RADIUS.sm};
                padding: 4px 12px;
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                color: {colors.text_primary};
                background-color: {colors.surface_hover};
                border-color: {colors.border};
            }}
            QPushButton:pressed {{
                backgroundColor: {colors.surface_active};
            }}
        """)
        btn.setCursor(Qt.PointingHandCursor)
        btn.clicked.connect(lambda checked=False, aid=action_id: self.action_triggered.emit(aid))
        # Insert before the trailing stretch to keep right-alignment
        layout = self.layout()
        if layout:
            last_idx = layout.count()
            layout.insertWidget(last_idx, btn)

    def remove_action(self, action_id: str) -> None:
        layout = self.layout()
        if layout:
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item and item.widget():
                    # Naive removal — best-effort
                    pass
