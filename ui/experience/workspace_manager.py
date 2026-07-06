from __future__ import annotations

import logging
from dataclasses import dataclass, field

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QStackedWidget, QWidget

from ui.command_center.theme import C

logger = logging.getLogger("experience.workspace")


@dataclass
class Workspace:
    workspace_id: str
    name: str
    widget: QWidget
    layout_state: dict = field(default_factory=dict)
    description: str = ""


class WorkspaceManager(QObject):
    workspace_created = Signal(str)
    workspace_switched = Signal(str, str)
    workspace_closed = Signal(str)
    workspace_renamed = Signal(str, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._workspaces: dict[str, Workspace] = {}
        self._stack: QStackedWidget | None = None
        self._current_id: str = ""

    def set_stack(self, stack: QStackedWidget) -> None:
        self._stack = stack

    def create(
        self,
        workspace_id: str,
        name: str,
        widget: QWidget | None = None,
        description: str = "",
    ) -> Workspace:
        if workspace_id in self._workspaces:
            logger.warning("Workspace '%s' already exists, reusing", workspace_id)
            return self._workspaces[workspace_id]

        content = widget or QWidget()
        if not widget:
            content.setStyleSheet(f"background-color: {C.BG};")

        ws = Workspace(
            workspace_id=workspace_id,
            name=name,
            widget=content,
            description=description,
        )
        self._workspaces[workspace_id] = ws
        if self._stack:
            self._stack.addWidget(content)
        self.workspace_created.emit(workspace_id)
        return ws

    def switch_to(self, workspace_id: str) -> bool:
        if workspace_id not in self._workspaces:
            logger.warning("Workspace '%s' not found", workspace_id)
            return False
        previous = self._current_id
        self._current_id = workspace_id
        ws = self._workspaces[workspace_id]
        if self._stack:
            self._stack.setCurrentWidget(ws.widget)
        self.workspace_switched.emit(previous, workspace_id)
        return True

    def close(self, workspace_id: str) -> bool:
        if workspace_id not in self._workspaces:
            return False
        ws = self._workspaces.pop(workspace_id)
        if self._stack:
            idx = self._stack.indexOf(ws.widget)
            if idx >= 0:
                self._stack.removeWidget(ws.widget)
        ws.widget.deleteLater()
        if self._current_id == workspace_id:
            remaining = list(self._workspaces.keys())
            self._current_id = remaining[0] if remaining else ""
            if self._current_id and self._stack:
                self._stack.setCurrentWidget(self._workspaces[self._current_id].widget)
        self.workspace_closed.emit(workspace_id)
        return True

    def rename(self, workspace_id: str, new_name: str) -> bool:
        ws = self._workspaces.get(workspace_id)
        if not ws:
            return False
        old_name = ws.name
        ws.name = new_name
        self.workspace_renamed.emit(workspace_id, old_name)
        return True

    @property
    def current(self) -> Workspace | None:
        return self._workspaces.get(self._current_id)

    @property
    def current_id(self) -> str:
        return self._current_id

    def get(self, workspace_id: str) -> Workspace | None:
        return self._workspaces.get(workspace_id)

    @property
    def all_workspaces(self) -> list[Workspace]:
        return list(self._workspaces.values())

    @property
    def workspace_names(self) -> list[str]:
        return [w.name for w in self._workspaces.values()]

    def save_state(self) -> dict:
        return {
            wid: {
                "name": ws.name,
                "description": ws.description,
                "layout_state": ws.layout_state,
            }
            for wid, ws in self._workspaces.items()
        }

    def load_state(self, state: dict) -> None:
        for wid, data in state.items():
            if wid in self._workspaces:
                ws = self._workspaces[wid]
                ws.name = data.get("name", ws.name)
                ws.description = data.get("description", ws.description)
                ws.layout_state = data.get("layout_state", {})

    def clear_all(self) -> None:
        for ws in list(self._workspaces.values()):
            if self._stack:
                idx = self._stack.indexOf(ws.widget)
                if idx >= 0:
                    self._stack.removeWidget(ws.widget)
            ws.widget.deleteLater()
        self._workspaces.clear()
        self._current_id = ""
