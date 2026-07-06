from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens
from ui.design_system.tokens.spacing import SpacingTokens

RADIUS = RadiusTokens()
SPACE = SpacingTokens()


class ChartContainer(QFrame):
    def __init__(
        self,
        title: str = "",
        subtitle: str = "",
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._build_ui(title, subtitle)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _build_ui(self, title: str, subtitle: str) -> None:
        colors = self._colors()
        self.setStyleSheet(f"""
            ChartContainer {{
                background-color: {colors.surface};
                border-radius: {RADIUS.lg};
                border: 1px solid {colors.border};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        if title:
            header = QHBoxLayout()
            header.setContentsMargins(0, 0, 0, 0)

            title_label = QLabel(title)
            title_label.setStyleSheet(
                f"color: {colors.text_primary}; font-size: 14px; font-weight: 600; "
                f"background: transparent; border: none;"
            )
            header.addWidget(title_label)

            if subtitle:
                sub = QLabel(subtitle)
                sub.setStyleSheet(
                    f"color: {colors.text_disabled}; font-size: 12px; "
                    f"background: transparent; border: none;"
                )
                header.addWidget(sub)

            header.addStretch()
            layout.addLayout(header)

        self._chart_area = QFrame()
        self._chart_area.setStyleSheet(
            "ChartContainer#chart_area { background: transparent; border: none; }"
        )
        self._chart_area.setObjectName("chart_area")
        chart_layout = QVBoxLayout(self._chart_area)
        chart_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._chart_area, 1)

    def set_chart(self, widget: QWidget) -> None:
        self._chart_area.layout().addWidget(widget)

    def clear_chart(self) -> None:
        layout = self._chart_area.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
