from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.command_center.theme import C, Font


class TimelineWidget(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background-color: transparent; border: none; }}
            QScrollBar:vertical {{ width: 4px; background: {C.SCROLLBAR_BG}; }}
            QScrollBar::handle:vertical {{ background: {C.SCROLLBAR_HANDLE}; border-radius: 2px; min-height: 20px; }}
        """)

        self._content = QWidget()
        self._content.setStyleSheet("background-color: transparent;")
        self._scroll_layout = QVBoxLayout(self._content)
        self._scroll_layout.setContentsMargins(0, 0, 0, 0)
        self._scroll_layout.setSpacing(2)
        self._scroll_layout.addStretch()

        scroll.setWidget(self._content)
        layout.addWidget(scroll)

    def add_item(self, date: str, title: str, subtitle: str = "",
                 color: str = C.ACCENT, icon: str = "") -> None:
        row = QFrame()
        row.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border-left: 2px solid {color};
                margin-left: 4px;
                padding: 6px 0 6px 12px;
            }}
        """)
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(8, 4, 8, 4)
        row_layout.setSpacing(8)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(1)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"color: {C.TEXT_PRIMARY}; font-size: 13px; font-weight: 600;")
        title_lbl.setWordWrap(True)
        text_layout.addWidget(title_lbl)

        if subtitle:
            sub_lbl = QLabel(subtitle)
            sub_lbl.setStyleSheet(Font.CAPTION)
            sub_lbl.setWordWrap(True)
            text_layout.addWidget(sub_lbl)

        date_lbl = QLabel(date)
        date_lbl.setStyleSheet(Font.CAPTION)
        date_lbl.setAlignment(Qt.AlignRight | Qt.AlignTop)

        row_layout.addLayout(text_layout, 1)
        row_layout.addWidget(date_lbl)

        self._scroll_layout.insertWidget(self._scroll_layout.count() - 1, row)

    def clear(self) -> None:
        while self._scroll_layout.count() > 1:
            item = self._scroll_layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
