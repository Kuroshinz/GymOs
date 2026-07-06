from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QWidget

from ui.command_center.theme import PAGE_LABELS, C


class Breadcrumb(QFrame):
    crumb_clicked = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._crumbs: list[str] = []
        self._build_ui()

    def _build_ui(self) -> None:
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(4)
        self.setStyleSheet("background-color: transparent;")

    def set_path(self, *pages: str) -> None:
        self._clear()
        self._crumbs = list(pages)
        for i, page in enumerate(pages):
            label = PAGE_LABELS.get(page, page.replace("_", " ").title())

            if i > 0:
                sep = QLabel("/")
                sep.setStyleSheet(f"color: {C.TEXT_MUTED}; font-size: 13px; padding: 0 2px;")
                self._layout.addWidget(sep)

            if i == len(pages) - 1:
                crumb = QLabel(label)
                crumb.setStyleSheet(f"color: {C.TEXT_PRIMARY}; font-size: 13px; font-weight: 600;")
            else:
                crumb = QPushButton(label)
                crumb.setStyleSheet(f"""
                    QPushButton {{
                        color: {C.TEXT_MUTED}; font-size: 13px;
                        background: transparent; border: none;
                        padding: 0; text-decoration: underline;
                    }}
                    QPushButton:hover {{ color: {C.ACCENT}; }}
                """)
                crumb.clicked.connect(lambda checked=False, p=page: self.crumb_clicked.emit(p))

            self._layout.addWidget(crumb)
        self._layout.addStretch()

    def _clear(self) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
