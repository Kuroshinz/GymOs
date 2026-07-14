from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens
from ui.design_system.tokens.typography import font_style

R = RadiusTokens()


@dataclass
class ActivityItem:
    icon: str = ""
    text: str = ""
    timestamp: str = ""
    status: str = ""
    status_color: str = ""


class ActivityFeed(QFrame):
    def __init__(
        self,
        items: list[ActivityItem] | None = None,
        title: str = "Recent Activity",
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._title = title
        self._items = items or []
        self.setAccessibleName(f"Activity feed: {title}")
        self._build_ui()

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _build_ui(self) -> None:
        colors = self._colors()
        self.setStyleSheet(f"""
            ActivityFeed {{
                background-color: {colors.surface};
                border-radius: {R.lg};
                border: 1px solid {colors.border};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(0)

        if self._title:
            t = QLabel(self._title)
            t.setStyleSheet(
                f"color: {colors.text_primary}; {font_style('body', weight='bold')}; "
                f"background: transparent; border: none;"
            )
            layout.addWidget(t)
            sep = QFrame()
            sep.setFixedHeight(1)
            sep.setStyleSheet(f"background-color: {colors.border}; border: none;")
            sep.setContentsMargins(0, 8, 0, 8)
            layout.addWidget(sep)

        for item in self._items:
            activity_widget = self._build_item(item)
            layout.addWidget(activity_widget)

    def _build_item(self, item: ActivityItem) -> QFrame:
        colors = self._colors()
        frame = QFrame()
        frame.setStyleSheet("ActivityFeed-item { background: transparent; border: none; }")

        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(10)

        if item.icon:
            icon_lbl = QLabel(item.icon)
            icon_lbl.setStyleSheet("font-size: 14px; background: transparent; border: none;")
            icon_lbl.setFixedWidth(20)
            layout.addWidget(icon_lbl)

        text_area = QVBoxLayout()
        text_area.setSpacing(2)

        text_lbl = QLabel(item.text)
        text_lbl.setStyleSheet(
            f"color: {colors.text_primary}; {font_style('body', weight=500)}; "
            f"background: transparent; border: none;"
        )
        text_lbl.setWordWrap(True)
        text_area.addWidget(text_lbl)

        if item.timestamp:
            ts_lbl = QLabel(item.timestamp)
            ts_lbl.setStyleSheet(
                f"color: {colors.text_disabled}; {font_style('label')}; "
                f"background: transparent; border: none;"
            )
            text_area.addWidget(ts_lbl)

        layout.addLayout(text_area, 1)

        if item.status:
            sc = item.status_color or colors.text_disabled
            status_lbl = QLabel(item.status)
            status_lbl.setStyleSheet(
                f"color: {sc}; {font_style('label')}; "
                f"background: transparent; border: none;"
            )
            layout.addWidget(status_lbl)

        sep = QFrame()
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {colors.border}; border: none;")
        frame._sep = sep

        return frame

    def set_items(self, items: list[ActivityItem]) -> None:
        self._items = items
        layout = self.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        self._build_ui()
