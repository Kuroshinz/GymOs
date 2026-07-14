from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ui.command_center.theme import C, Font

COMMANDS: list[tuple[str, str, str]] = [
    ("Go to Home", "home", "Navigate to the Home dashboard"),
    ("Go to Mission", "mission", "View today's mission and workout"),
    ("Go to Planning", "planning", "Macrocycle, mesocycle, week planning"),
    ("Go to Prediction Center", "prediction", "Forecast and trend analysis"),
    ("Go to Recovery Center", "recovery", "Recovery score and readiness"),
    ("Go to Knowledge Center", "knowledge", "Knowledge evolution and insights"),
    ("Go to Adaptive Center", "adaptive", "Adaptation strategies and timeline"),
    ("Go to Analytics Center", "analytics", "Volume, nutrition, PR, compliance"),
    ("Go to AI Briefing Center", "intelligence", "AI insights, briefing, and configuration"),
    ("Go to System Center", "system", "Capabilities, kernel, release info"),
    ("Refresh All Data", "_refresh", "Refresh every widget from canonical services"),
    ("Toggle Dark Mode", "_theme", "Toggle between light and dark theme"),
]


class CommandPalette(QDialog):
    command_selected = Signal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Command Palette")
        self.setModal(True)
        self.setFixedSize(500, 320)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {C.CARD_BG};
                border: 1px solid {C.BORDER};
                border-radius: 16px;
            }}
        """)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Type a command...")
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {C.SIDEBAR_BG};
                color: {C.TEXT_PRIMARY};
                border: 1px solid {C.BORDER};
                border-radius: 8px;
                font-size: 14px;
                padding: 10px 14px;
            }}
            QLineEdit::placeholder {{ color: {C.TEXT_MUTED}; }}
            QLineEdit:focus {{ border-color: {C.ACCENT}; }}
        """)
        self._input.textChanged.connect(self._filter)
        layout.addWidget(self._input)

        self._list = QListWidget()
        self._list.setStyleSheet(f"""
            QListWidget {{
                background-color: transparent;
                border: none;
                font-size: 13px;
            }}
            QListWidget::item {{
                color: {C.TEXT_SECONDARY};
                padding: 8px 12px;
                border-radius: 6px;
            }}
            QListWidget::item:hover, QListWidget::item:selected {{
                background-color: {C.SIDEBAR_HOVER};
                color: {C.TEXT_PRIMARY};
            }}
        """)
        self._list.itemClicked.connect(self._execute)
        self._list.itemDoubleClicked.connect(self._execute)
        layout.addWidget(self._list, 1)

        hint = QLabel("↑↓ navigate  ·  Enter to select  ·  Esc to close")
        hint.setStyleSheet(Font.CAPTION)
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

        self._populate(COMMANDS)

    def _populate(self, commands: list[tuple[str, str, str]]) -> None:
        self._list.clear()
        for label, cmd, desc in commands:
            item = QListWidgetItem(f"  {label}")
            item.setData(Qt.UserRole, cmd)
            item.setToolTip(desc)
            self._list.addItem(item)

    def _filter(self, text: str) -> None:
        text = text.strip().lower()
        filtered = [(_label, c, d) for _label, c, d in COMMANDS if text in _label.lower() or text in d.lower()] if text else COMMANDS
        self._populate(filtered)

    def _execute(self, item: QListWidgetItem) -> None:
        cmd = item.data(Qt.UserRole)
        if cmd:
            self.command_selected.emit(cmd)
            self.accept()

    def keyPressEvent(self, event: QKeyEvent | None) -> None:  # noqa: N802
        if event and event.key() == Qt.Key_Escape:
            self.reject()
        elif event and event.key() == Qt.Key_Return and self._list.currentItem():
            self._execute(self._list.currentItem())
        else:
            super().keyPressEvent(event)

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._input.setFocus()
        self._input.selectAll()
