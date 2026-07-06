from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QWidget

logger = logging.getLogger("experience.shortcuts")


@dataclass
class Shortcut:
    shortcut_id: str
    key_sequence: str
    callback: Callable[[], None] | None = None
    description: str = ""
    category: str = "general"
    context: str = "global"
    widget: QWidget | None = None


class ShortcutManager(QObject):
    shortcut_triggered = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._shortcuts: dict[str, Shortcut] = {}
        self._qt_shortcuts: dict[str, QShortcut] = {}
        self._contexts: dict[str, list[str]] = {"global": []}

    def register(self, shortcut: Shortcut) -> None:
        self._shortcuts[shortcut.shortcut_id] = shortcut

        context_list = self._contexts.setdefault(shortcut.context, [])
        context_list.append(shortcut.shortcut_id)

        parent = shortcut.widget or self._parent_widget()
        if parent is None:
            logger.warning("No parent widget for shortcut '%s'", shortcut.shortcut_id)
            return

        qt_shortcut = QShortcut(QKeySequence(shortcut.key_sequence), parent)
        if shortcut.callback:
            qt_shortcut.activated.connect(shortcut.callback)
        qt_shortcut.activated.connect(lambda: self.shortcut_triggered.emit(shortcut.shortcut_id))
        self._qt_shortcuts[shortcut.shortcut_id] = qt_shortcut

    def unregister(self, shortcut_id: str) -> None:
        self._shortcuts.pop(shortcut_id, None)
        qt_shortcut = self._qt_shortcuts.pop(shortcut_id, None)
        if qt_shortcut:
            qt_shortcut.setEnabled(False)
            qt_shortcut.deleteLater()
        for context_list in self._contexts.values():
            if shortcut_id in context_list:
                context_list.remove(shortcut_id)

    def register_many(self, shortcuts: list[Shortcut]) -> None:
        for s in shortcuts:
            self.register(s)

    def enable_context(self, context: str) -> None:
        shortcut_ids = self._contexts.get(context, [])
        for sid in shortcut_ids:
            qt_shortcut = self._qt_shortcuts.get(sid)
            if qt_shortcut:
                qt_shortcut.setEnabled(True)

    def disable_context(self, context: str) -> None:
        shortcut_ids = self._contexts.get(context, [])
        for sid in shortcut_ids:
            qt_shortcut = self._qt_shortcuts.get(sid)
            if qt_shortcut:
                qt_shortcut.setEnabled(False)

    def get_by_category(self, category: str) -> list[Shortcut]:
        return [s for s in self._shortcuts.values() if s.category == category]

    def get_by_context(self, context: str) -> list[Shortcut]:
        shortcut_ids = self._contexts.get(context, [])
        return [self._shortcuts[sid] for sid in shortcut_ids if sid in self._shortcuts]

    def search(self, query: str) -> list[Shortcut]:
        q = query.lower()
        return [
            s for s in self._shortcuts.values()
            if q in s.description.lower() or q in s.shortcut_id.lower() or q in s.category.lower()
        ]

    @property
    def all_shortcuts(self) -> list[Shortcut]:
        return list(self._shortcuts.values())

    def clear_all(self) -> None:
        for qt_shortcut in self._qt_shortcuts.values():
            qt_shortcut.setEnabled(False)
            qt_shortcut.deleteLater()
        self._shortcuts.clear()
        self._qt_shortcuts.clear()
        self._contexts.clear()
        self._contexts["global"] = []

    def _parent_widget(self) -> QWidget | None:
        parent = self.parent()
        if isinstance(parent, QWidget):
            return parent
        return None
