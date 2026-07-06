from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ui.command_center.theme import C, Font

SEARCH_ITEMS = {
    "home": ["home", "dashboard", "overview"],
    "mission": ["mission", "today", "workout", "session"],
    "planning": ["planning", "macrocycle", "mesocycle", "week", "optimizer"],
    "prediction": ["prediction", "forecast", "trend", "projection"],
    "recovery": ["recovery", "readiness", "fatigue", "deload"],
    "knowledge": ["knowledge", "evolution", "insight", "pattern"],
    "adaptive": ["adaptive", "strategy", "adaptation", "timeline"],
    "analytics": ["analytics", "volume", "nutrition", "pr", "compliance"],
    "system": ["system", "capability", "kernel", "release", "health"],
}


class QuickSearch(QFrame):
    navigated = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        self.setStyleSheet(f"""
            QuickSearch {{
                background-color: {C.CARD_BG};
                border-radius: 8px;
                border: 1px solid {C.BORDER};
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(12, 8, 12, 8)
        search_layout.setSpacing(8)

        icon = QLabel("🔍")
        search_layout.addWidget(icon)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Search pages, widgets, commands...")
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background-color: transparent;
                color: {C.TEXT_PRIMARY};
                border: none;
                font-size: 13px;
                padding: 4px 0;
            }}
            QLineEdit::placeholder {{ color: {C.TEXT_MUTED}; }}
        """)
        self._input.textChanged.connect(self._on_search)
        search_layout.addWidget(self._input, 1)

        shortcut = QLabel("Ctrl+K")
        shortcut.setStyleSheet(Font.CAPTION)
        search_layout.addWidget(shortcut)

        layout.addLayout(search_layout)

        self._results = QListWidget()
        self._results.setVisible(False)
        self._results.setMaximumHeight(200)
        self._results.setStyleSheet(f"""
            QListWidget {{
                background-color: {C.CARD_BG};
                border: none;
                border-top: 1px solid {C.BORDER};
                padding: 4px;
            }}
            QListWidget::item {{
                color: {C.TEXT_SECONDARY};
                padding: 6px 12px;
                border-radius: 4px;
            }}
            QListWidget::item:hover, QListWidget::item:selected {{
                background-color: {C.SIDEBAR_HOVER};
                color: {C.TEXT_PRIMARY};
            }}
        """)
        self._results.itemClicked.connect(lambda item: self._navigate(item))
        layout.addWidget(self._results)

    def _on_search(self, text: str) -> None:
        text = text.strip().lower()
        self._results.clear()
        if not text or len(text) < 2:
            self._results.setVisible(False)
            return

        matches = []
        for page_id, keywords in SEARCH_ITEMS.items():
            for kw in keywords:
                if text in kw:
                    matches.append((page_id, kw))
                    break

        if matches:
            self._results.setVisible(True)
            for page_id, kw in matches:
                item = QListWidgetItem(f"  {kw.title()}  →  {page_id.replace('_', ' ').title()}")
                item.setData(Qt.UserRole, page_id)
                self._results.addItem(item)
        else:
            self._results.setVisible(False)

    def _navigate(self, item: QListWidgetItem) -> None:
        page_id = item.data(Qt.UserRole)
        if page_id:
            self._input.clear()
            self._results.setVisible(False)
            self.navigated.emit(page_id)

    def focus(self) -> None:
        self._input.setFocus()
        self._input.selectAll()

    def clear_search(self) -> None:
        self._input.clear()
        self._results.setVisible(False)
