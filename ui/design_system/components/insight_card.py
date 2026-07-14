from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.design_system.components.status_badge import StatusBadge, StatusLevel
from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens

R = RadiusTokens()


class InsightCard(QFrame):
    clicked = Signal()

    def __init__(
        self,
        icon: str = "",
        title: str = "",
        description: str = "",
        badge_text: str = "",
        badge_level: StatusLevel = StatusLevel.INFO,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self.setObjectName("InsightCard")
        self._build_ui(icon, title, description, badge_text, badge_level)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _build_ui(self, icon: str, title: str, description: str, badge_text: str, badge_level: StatusLevel) -> None:
        colors = self._colors()
        self.setStyleSheet(f"""
            InsightCard {{
                background-color: {colors.surface};
                border-radius: {R.md};
                border: 1px solid {colors.border};
            }}
            InsightCard:hover {{
                border-color: {colors.border_hover};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        if icon:
            icon_lbl = QLabel(icon)
            icon_lbl.setStyleSheet("font-size: 20px; background: transparent; border: none;")
            icon_lbl.setFixedWidth(28)
            layout.addWidget(icon_lbl)

        text_area = QVBoxLayout()
        text_area.setSpacing(4)

        top = QHBoxLayout()
        top.setSpacing(8)

        t = QLabel(title)
        t.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 13px; font-weight: 600; "
            f"background: transparent; border: none;"
        )
        t.setWordWrap(True)
        top.addWidget(t, 1)

        if badge_text:
            badge = StatusBadge(text=badge_text, level=badge_level, outlined=True)
            top.addWidget(badge)

        text_area.addLayout(top)

        if description:
            d = QLabel(description)
            d.setStyleSheet(
                f"color: {colors.text_secondary}; font-size: 12px; "
                f"background: transparent; border: none;"
            )
            d.setWordWrap(True)
            text_area.addWidget(d)

        layout.addLayout(text_area, 1)
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):  # noqa: N802
        super().mousePressEvent(event)
        self.clicked.emit()
