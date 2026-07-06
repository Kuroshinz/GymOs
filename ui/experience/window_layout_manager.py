from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QMainWindow

logger = logging.getLogger("experience.window_layout")


@dataclass
class WindowState:
    geometry: dict = field(default_factory=dict)
    window_state: str = "normal"
    splitter_states: dict = field(default_factory=dict)
    dock_states: dict = field(default_factory=dict)
    active_workspace: str = "default"


class WindowLayoutManager(QObject):
    state_saved = Signal(str)
    state_restored = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._states: dict[str, WindowState] = {}
        self._save_key = "gymos_window_layout"

    def save_current(self, name: str = "default") -> WindowState:
        state = WindowState()
        window = self._main_window()
        if window:
            geo = window.geometry()
            state.geometry = {
                "x": geo.x(), "y": geo.y(),
                "width": geo.width(), "height": geo.height(),
            }
            state.window_state = "maximized" if window.isMaximized() else "normal"
        self._states[name] = state
        self.state_saved.emit(name)
        return state

    def restore(self, name: str = "default") -> bool:
        state = self._states.get(name)
        if not state:
            return False
        window = self._main_window()
        if window and state.geometry:
            geo = state.geometry
            window.setGeometry(geo.get("x", 0), geo.get("y", 0), geo.get("width", 1280), geo.get("height", 800))
            if state.window_state == "maximized":
                window.showMaximized()
        self.state_restored.emit(name)
        return True

    def save_persistent(self) -> None:
        state = self.save_current()
        from PySide6.QtCore import QSettings
        settings = QSettings("GymOS", "Experience")
        settings.setValue(self._save_key, json.dumps({
            "geometry": state.geometry,
            "window_state": state.window_state,
        }))

    def load_persistent(self) -> bool:
        from PySide6.QtCore import QSettings
        settings = QSettings("GymOS", "Experience")
        raw = settings.value(self._save_key, "")
        if not raw:
            return False
        try:
            data = json.loads(raw) if isinstance(raw, str) else raw
            state = WindowState(
                geometry=data.get("geometry", {}),
                window_state=data.get("window_state", "normal"),
            )
            self._states["default"] = state
            return self.restore("default")
        except (json.JSONDecodeError, TypeError, AttributeError):
            logger.warning("Failed to load persistent window state")
            return False

    def save_state(self, name: str) -> dict:
        state = self.save_current(name)
        return {
            "geometry": state.geometry,
            "window_state": state.window_state,
            "splitter_states": state.splitter_states,
            "dock_states": state.dock_states,
            "active_workspace": state.active_workspace,
        }

    def load_state(self, name: str, data: dict) -> bool:
        try:
            state = WindowState(
                geometry=data.get("geometry", {}),
                window_state=data.get("window_state", "normal"),
                splitter_states=data.get("splitter_states", {}),
                dock_states=data.get("dock_states", {}),
                active_workspace=data.get("active_workspace", "default"),
            )
            self._states[name] = state
            return self.restore(name)
        except Exception:
            logger.warning("Failed to load state '%s'", name)
            return False

    def list_saved_states(self) -> list[str]:
        return list(self._states.keys())

    def delete_state(self, name: str) -> None:
        self._states.pop(name, None)

    def _main_window(self) -> QMainWindow | None:
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QMainWindow):
                return widget
        return None
