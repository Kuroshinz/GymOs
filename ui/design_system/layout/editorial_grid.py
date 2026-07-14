from __future__ import annotations

from enum import Enum

from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens
from ui.design_system.tokens.spacing import SpacingTokens

S = SpacingTokens()
R = RadiusTokens()


class PanelSpan(Enum):
    FULL = "full"
    HALF = "half"
    THIRD = "third"
    TWO_THIRDS = "two_thirds"
    QUARTER = "quarter"
    HERO = "hero"


_SPAN_COLUMNS = {
    PanelSpan.FULL: 12,
    PanelSpan.HERO: 12,
    PanelSpan.TWO_THIRDS: 8,
    PanelSpan.HALF: 6,
    PanelSpan.THIRD: 4,
    PanelSpan.QUARTER: 3,
}


class HeroPanel(QFrame):
    def __init__(
        self,
        title: str = "",
        subtitle: str = "",
        accent_color: str = "",
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self.setObjectName("HeroPanel")
        self._accent = accent_color
        self._build_ui(title, subtitle)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _build_ui(self, title: str, subtitle: str) -> None:
        colors = self._colors()
        accent = self._accent or colors.primary
        self.setStyleSheet(f"""
            HeroPanel {{
                background-color: {colors.surface};
                border-radius: {R.xl};
                border: 1px solid {colors.border};
            }}
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        accent_bar = QFrame()
        accent_bar.setFixedWidth(4)
        accent_bar.setStyleSheet(f"background-color: {accent}; border-radius: 2px; border: none;")
        layout.addWidget(accent_bar)

        text_area = QVBoxLayout()
        text_area.setSpacing(6)

        t = QLabel(title)
        t.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 20px; font-weight: 700; "
            f"background: transparent; border: none;"
        )
        text_area.addWidget(t)

        sub = QLabel(subtitle)
        sub.setStyleSheet(
            f"color: {colors.text_secondary}; font-size: 14px; "
            f"background: transparent; border: none;"
        )
        sub.setWordWrap(True)
        text_area.addWidget(sub)

        text_area.addStretch()
        layout.addLayout(text_area, 1)

        self._content_area = QHBoxLayout()
        self._content_area.setSpacing(12)
        layout.addLayout(self._content_area)

    def add_content(self, widget: QWidget) -> None:
        self._content_area.addWidget(widget)


class MetricPanel(QFrame):
    def __init__(
        self,
        value: str = "",
        label: str = "",
        icon: str = "",
        trend: str = "",
        trend_color: str = "",
        accent_color: str = "",
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self.setObjectName("MetricPanel")
        self._build_ui(value, label, icon, trend, trend_color, accent_color)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _build_ui(self, value: str, label: str, icon: str, trend: str, trend_color: str, accent_color: str) -> None:
        colors = self._colors()
        self.setStyleSheet(f"""
            MetricPanel {{
                background-color: {colors.surface};
                border-radius: {R.lg};
                border: 1px solid {colors.border};
            }}
            MetricPanel:hover {{
                border-color: {colors.border_hover};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(4)

        if icon:
            top_row = QHBoxLayout()
            top_row.setContentsMargins(0, 0, 0, 0)
            icon_label = QLabel(icon)
            icon_label.setStyleSheet("font-size: 18px; background: transparent; border: none;")
            top_row.addWidget(icon_label)

            if trend:
                t = QLabel(trend)
                tc = trend_color or colors.text_disabled
                t.setStyleSheet(f"color: {tc}; font-size: 12px; font-weight: 600; background: transparent; border: none;")
                top_row.addWidget(t)

            top_row.addStretch()
            layout.addLayout(top_row)

        v = QLabel(value)
        v.setStyleSheet(f"color: {colors.text_primary}; font-size: 28px; font-weight: 800; background: transparent; border: none;")
        layout.addWidget(v)

        if label:
            _label = QLabel(label)
            _label.setStyleSheet(f"color: {colors.text_disabled}; font-size: 12px; font-weight: 500; background: transparent; border: none;")
            layout.addWidget(_label)


class SectionPanel(QFrame):
    def __init__(
        self,
        title: str = "",
        subtitle: str = "",
        span: PanelSpan = PanelSpan.FULL,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._span = span
        self.setObjectName("SectionPanel")
        self._build_ui(title, subtitle)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _build_ui(self, title: str, subtitle: str) -> None:
        colors = self._colors()
        self.setStyleSheet(f"""
            SectionPanel {{
                background-color: {colors.surface};
                border-radius: {R.lg};
                border: 1px solid {colors.border};
            }}
            SectionPanel:hover {{
                border-color: {colors.border_hover};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        if title or subtitle:
            header = QVBoxLayout()
            header.setSpacing(2)

            if title:
                t = QLabel(title)
                t.setStyleSheet(f"color: {colors.text_primary}; font-size: 16px; font-weight: 700; background: transparent; border: none;")
                header.addWidget(t)

            if subtitle:
                s = QLabel(subtitle)
                s.setStyleSheet(f"color: {colors.text_secondary}; font-size: 12px; background: transparent; border: none;")
                header.addWidget(s)

            layout.addLayout(header)

        self._body = QVBoxLayout()
        self._body.setSpacing(8)
        layout.addLayout(self._body)

    def span(self) -> PanelSpan:
        return self._span

    def add_content(self, widget: QWidget) -> None:
        self._body.addWidget(widget)

    def add_layout(self, layout) -> None:
        self._body.addLayout(layout)

    def clear(self) -> None:
        while self._body.count():
            item = self._body.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            if item.layout():
                while item.layout().count():
                    c = item.layout().takeAt(0)
                    if c.widget():
                        c.widget().deleteLater()


class EditorialGrid(QFrame):
    GRID_COLUMNS = 12

    def __init__(
        self,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._panels: list[QWidget] = []
        self._grid = QGridLayout()
        self._grid.setContentsMargins(0, 0, 0, 0)
        self._grid.setSpacing(16)
        self.setLayout(self._grid)
        self.setStyleSheet("EditorialGrid { background: transparent; border: none; }")

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def add_panel(self, panel: QWidget, span: PanelSpan = PanelSpan.FULL) -> None:
        cols = _SPAN_COLUMNS.get(span, 12)
        row = self._find_next_row()
        self._grid.addWidget(panel, row, 0, 1, cols)

    def add_section(self, section: SectionPanel) -> None:
        cols = _SPAN_COLUMNS.get(section._span, 12)
        row = self._find_next_row()
        self._grid.addWidget(section, row, 0, 1, cols)
        self._panels.append(section)

    def _find_next_row(self) -> int:
        return self._grid.rowCount()

    def add_row(self, sections: list[tuple[SectionPanel, PanelSpan]]) -> None:
        row = self._find_next_row()
        col = 0
        for section, span in sections:
            cols = _SPAN_COLUMNS.get(span, 6)
            self._grid.addWidget(section, row, col, 1, cols)
            col += cols
            self._panels.append(section)

    def clear(self) -> None:
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._panels.clear()

    def set_spacing(self, spacing: int) -> None:
        self._grid.setSpacing(spacing)
