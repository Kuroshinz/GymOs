from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ui.command_center.theme import C

logger = logging.getLogger("experience.command_palette")


@dataclass
class CommandItem:
    command_id: str
    label: str
    description: str = ""
    category: str = "general"
    shortcut: str = ""
    icon: str = ""
    callback: Callable[[], None] | None = None
    enabled: bool = True


class CommandPaletteDialog(QDialog):
    command_executed = Signal(str)

    def __init__(self, commands: list[CommandItem], parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._commands = commands
        self._filtered: list[CommandItem] = commands[:]
        self._build_ui()

    def _build_ui(self) -> None:
        self.setWindowTitle("Command Palette")
        self.setMinimumSize(500, 400)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {C.BG};
                border: 1px solid {C.BORDER};
                border-radius: 12px;
            }}
        """)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        search_frame = QFrame()
        search_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {C.CARD_BG};
                border-bottom: 1px solid {C.BORDER};
                border-radius: 12px 12px 0 0;
            }}
        """)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(16, 12, 16, 12)

        icon_label = QLabel("🔍")
        icon_label.setStyleSheet("font-size: 16px;")
        search_layout.addWidget(icon_label)

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("Search commands...")
        self._search_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: transparent;
                color: {C.TEXT_PRIMARY};
                border: none;
                font-size: 16px;
                padding: 4px 8px;
            }}
            QLineEdit:focus {{
                border: none;
            }}
        """)
        self._search_input.textChanged.connect(self._filter)
        search_layout.addWidget(self._search_input, 1)

        layout.addWidget(search_frame)

        self._list = QListWidget()
        self._list.setStyleSheet(f"""
            QListWidget {{
                background-color: {C.BG};
                border: none;
                outline: none;
                padding: 4px;
            }}
            QListWidget::item {{
                color: {C.TEXT_PRIMARY};
                padding: 10px 16px;
                border-radius: 6px;
                border: none;
            }}
            QListWidget::item:hover {{
                background-color: {C.CARD_BG};
            }}
            QListWidget::item:selected {{
                background-color: {C.ACCENT};
                color: #FFFFFF;
            }}
        """)
        layout.addWidget(self._list, 1)

        self._populate()
        self._search_input.setFocus()
        self._list.itemClicked.connect(self._on_item_clicked)
        self._list.itemDoubleClicked.connect(self._on_item_clicked)

    def _populate(self) -> None:
        self._list.clear()
        for cmd in self._filtered:
            display = cmd.label
            if cmd.shortcut:
                display = f"{cmd.label}  [{cmd.shortcut}]"
            item = QListWidgetItem(display)
            item.setData(Qt.ItemDataRole.UserRole, cmd.command_id)
            if not cmd.enabled:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self._list.addWidget(item) if False else self._list.addItem(item)

    def _filter(self, text: str) -> None:
        q = text.lower().strip()
        if not q:
            self._filtered = self._commands[:]
        else:
            self._filtered = [
                c for c in self._commands
                if q in c.label.lower() or q in c.description.lower() or q in c.category.lower()
            ]
        self._populate()
        if self._list.count() > 0:
            self._list.setCurrentRow(0)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        cmd_id = item.data(Qt.ItemDataRole.UserRole)
        if cmd_id:
            self.command_executed.emit(cmd_id)
            self.accept()


class CommandPaletteEngine(QObject):
    command_registered = Signal(str)
    command_unregistered = Signal(str)
    command_executed = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._commands: dict[str, CommandItem] = {}

    def register(self, command: CommandItem) -> None:
        self._commands[command.command_id] = command
        self.command_registered.emit(command.command_id)

    def register_many(self, commands: list[CommandItem]) -> None:
        for cmd in commands:
            self._commands[cmd.command_id] = cmd
        self.command_registered.emit(f"{len(commands)}_batch")

    def unregister(self, command_id: str) -> None:
        self._commands.pop(command_id, None)
        self.command_unregistered.emit(command_id)

    def get(self, command_id: str) -> CommandItem | None:
        return self._commands.get(command_id)

    def search(self, query: str) -> list[CommandItem]:
        q = query.lower().strip()
        if not q:
            return []
        return [
            c for c in self._commands.values()
            if q in c.label.lower() or q in c.description.lower() or q in c.category.lower()
        ]

    def get_by_category(self, category: str) -> list[CommandItem]:
        return [c for c in self._commands.values() if c.category == category]

    def execute(self, command_id: str) -> bool:
        cmd = self._commands.get(command_id)
        if not cmd or not cmd.enabled:
            return False
        if cmd.callback:
            cmd.callback()
        self.command_executed.emit(command_id)
        return True

    def open_palette(self, parent: QWidget | None = None) -> None:
        commands = list(self._commands.values())
        dialog = CommandPaletteDialog(commands, parent)
        dialog.command_executed.connect(self.execute)
        dialog.exec()

    @property
    def all_commands(self) -> list[CommandItem]:
        return list(self._commands.values())

    @property
    def count(self) -> int:
        return len(self._commands)

    def categories(self) -> list[str]:
        cats: list[str] = []
        for cmd in self._commands.values():
            if cmd.category not in cats:
                cats.append(cmd.category)
        return cats
