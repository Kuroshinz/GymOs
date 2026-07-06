from __future__ import annotations

import logging

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget

logger = logging.getLogger("experience.focus")


class FocusMode(QObject):
    focus_entered = Signal()
    focus_exited = Signal()
    focus_toggled = Signal(bool)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._active = False
        self._hidden_widgets: list[QWidget] = []
        self._sidebar: QWidget | None = None
        self._top_bar: QWidget | None = None
        self._background_style = ""

    def register_sidebar(self, sidebar: QWidget) -> None:
        self._sidebar = sidebar

    def register_top_bar(self, top_bar: QWidget) -> None:
        self._top_bar = top_bar

    def register_hideable(self, widget: QWidget) -> None:
        self._hidden_widgets.append(widget)

    @property
    def is_active(self) -> bool:
        return self._active

    def enter(self) -> None:
        if self._active:
            return
        self._active = True
        if self._sidebar:
            self._sidebar.hide()
        if self._top_bar:
            self._top_bar.hide()
        for w in self._hidden_widgets:
            w.hide()
        self.focus_entered.emit()
        self.focus_toggled.emit(True)

    def exit(self) -> None:
        if not self._active:
            return
        self._active = False
        if self._sidebar:
            self._sidebar.show()
        if self._top_bar:
            self._top_bar.show()
        for w in self._hidden_widgets:
            w.show()
        self.focus_exited.emit()
        self.focus_toggled.emit(False)

    def toggle(self) -> None:
        if self._active:
            self.exit()
        else:
            self.enter()
