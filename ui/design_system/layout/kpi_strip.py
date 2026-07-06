from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens
from ui.design_system.tokens.spacing import SpacingTokens

S = SpacingTokens()
R = RadiusTokens()


@dataclass
class KpiItem:
    label: str = ""
    value: str = ""
    unit: str = ""
    trend: str = ""
    trend_color: str = ""
    accent: str = ""


class KpiStrip(QFrame):
    item_clicked = Signal(int)

    def __init__(
        self,
        items: list[KpiItem] | None = None,
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._items = items or []
        self._kpi_widgets: list[QFrame] = []
        self._build_ui()

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _build_ui(self) -> None:
        colors = self._colors()
        self.setStyleSheet("KpiStrip { background: transparent; border: none; }")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(1)

        for i, item in enumerate(self._items):
            kpi = self._build_kpi(item)
            self._kpi_widgets.append(kpi)
            layout.addWidget(kpi, 1)
            if i < len(self._items) - 1:
                sep = QFrame()
                sep.setFixedWidth(1)
                sep.setStyleSheet(f"background-color: {colors.border}; border: none;")
                layout.addWidget(sep)

    def _build_kpi(self, item: KpiItem) -> QFrame:
        colors = self._colors()
        accent = item.accent or colors.text_primary
        frame = QFrame()
        frame.setStyleSheet(f"""
            KpiStrip--item {{
                background-color: transparent;
                border: none;
            }}
            KpiStrip--item:hover {{
                background-color: {colors.surface};
            }}
        """)
        frame.setCursor(Qt.PointingHandCursor)
        frame._kpi_index = len(self._kpi_widgets)

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignCenter)

        top = QHBoxLayout()
        top.setSpacing(4)
        top.setAlignment(Qt.AlignCenter)

        v = QLabel(item.value)
        v.setStyleSheet(
            f"color: {accent}; font-size: 20px; font-weight: 800; "
            f"background: transparent; border: none;"
        )
        top.addWidget(v)

        if item.unit:
            u = QLabel(item.unit)
            u.setStyleSheet(
                f"color: {colors.text_disabled}; font-size: 11px; font-weight: 500; "
                f"background: transparent; border: none;"
            )
            top.addWidget(u)

        if item.trend:
            tc = item.trend_color or colors.text_disabled
            t = QLabel(item.trend)
            t.setStyleSheet(
                f"color: {tc}; font-size: 12px; font-weight: 700; "
                f"background: transparent; border: none;"
            )
            top.addWidget(t)

        layout.addLayout(top)

        if item.label:
            l = QLabel(item.label)
            l.setStyleSheet(
                f"color: {colors.text_disabled}; font-size: 10px; font-weight: 500; "
                f"background: transparent; border: none;"
            )
            l.setAlignment(Qt.AlignCenter)
            layout.addWidget(l)

        frame.mousePressEvent = lambda event, idx=frame._kpi_index: self._on_kpi_clicked(event, idx)
        return frame

    def _on_kpi_clicked(self, event, index: int) -> None:
        self.item_clicked.emit(index)

    def set_items(self, items: list[KpiItem]) -> None:
        self._items = items
        for w in self._kpi_widgets:
            w.deleteLater()
        self._kpi_widgets.clear()
        layout = self.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        for i, item in enumerate(self._items):
            kpi = self._build_kpi(item)
            self._kpi_widgets.append(kpi)
            layout.addWidget(kpi, 1)
            if i < len(self._items) - 1:
                colors = self._colors()
                sep = QFrame()
                sep.setFixedWidth(1)
                sep.setStyleSheet(f"background-color: {colors.border}; border: none;")
                layout.addWidget(sep)
