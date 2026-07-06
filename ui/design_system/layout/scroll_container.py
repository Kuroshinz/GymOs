from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QScrollArea, QVBoxLayout, QWidget

from ui.design_system.tokens.color import ColorScheme, color_from_scheme


class ScrollContainer(QScrollArea):
    def __init__(
        self,
        content: QWidget | None = None,
        padding: str = "32px",
        color_scheme: ColorScheme = ColorScheme.DARK,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._color_scheme = color_scheme
        self._build_ui(content, padding)

    def _colors(self):
        return color_from_scheme(self._color_scheme)

    def _build_ui(self, content: QWidget | None, padding: str) -> None:
        colors = self._colors()
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setStyleSheet(f"""
            QScrollArea {{
                background-color: {colors.background};
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {colors.scrollbar_bg};
                width: 8px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background-color: {colors.scrollbar_handle};
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {colors.scrollbar_hover};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

        self._wrapper = QFrame()
        self._wrapper.setStyleSheet(f"background-color: {colors.background}; border: none;")
        wrapper_layout = QVBoxLayout(self._wrapper)
        wrapper_layout.setContentsMargins(32, 24, 32, 32)
        wrapper_layout.setSpacing(0)

        if content:
            wrapper_layout.addWidget(content)

        wrapper_layout.addStretch()
        self.setWidget(self._wrapper)

    @property
    def content_layout(self) -> QVBoxLayout:
        return self._wrapper.layout()

    def set_content(self, widget: QWidget) -> None:
        layout = self._wrapper.layout()
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        layout.insertWidget(0, widget)
        layout.addStretch()
