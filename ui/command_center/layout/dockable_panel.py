from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.command_center.theme import C, Font


class DockablePanel(QFrame):
    closed = Signal(str)

    def __init__(self, title: str = "", panel_id: str = "",
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._panel_id = panel_id or title.lower().replace(" ", "_")
        self._title = title
        self._docked = True
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            DockablePanel {{
                background-color: {C.CARD_BG};
                border-radius: 12px;
                border: 1px solid {C.BORDER};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border-bottom: 1px solid {C.BORDER};
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }}
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(14, 8, 8, 8)
        header_layout.setSpacing(8)

        title_label = QLabel(self._title)
        title_label.setStyleSheet(Font.LABEL)
        header_layout.addWidget(title_label, 1)

        self._dock_btn = QPushButton("⤓")
        self._dock_btn.setFixedSize(24, 24)
        self._dock_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {C.TEXT_MUTED};
                border: none; font-size: 14px;
            }}
            QPushButton:hover {{ color: {C.TEXT_PRIMARY}; }}
        """)
        self._dock_btn.clicked.connect(self._toggle_dock)
        header_layout.addWidget(self._dock_btn)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent; color: {C.TEXT_MUTED};
                border: none; font-size: 12px;
            }}
            QPushButton:hover {{ color: {C.TEXT_DANGER}; }}
        """)
        close_btn.clicked.connect(lambda: self.closed.emit(self._panel_id))
        header_layout.addWidget(close_btn)

        layout.addWidget(header)

        self._content = QWidget()
        self._content.setStyleSheet("background-color: transparent;")
        self._content_layout = QVBoxLayout(self._content)
        self._content_layout.setContentsMargins(14, 10, 14, 10)
        self._content_layout.setSpacing(8)
        layout.addWidget(self._content, 1)

    def set_content(self, widget: QWidget) -> None:
        self._content_layout.addWidget(widget)

    def content_layout(self) -> QVBoxLayout:
        return self._content_layout

    def _toggle_dock(self) -> None:
        self._docked = not self._docked
        self._dock_btn.setText("⤒" if self._docked else "⤓")

    @property
    def panel_id(self) -> str:
        return self._panel_id

    @property
    def is_docked(self) -> bool:
        return self._docked
