from __future__ import annotations

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget


class AccessibilityManager(QObject):
    high_contrast_changed = Signal(bool)
    reduced_motion_changed = Signal(bool)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._high_contrast = False
        self._reduced_motion = False
        self._reduced_motion_widgets: list[QWidget] = []

    @property
    def high_contrast(self) -> bool:
        return self._high_contrast

    @property
    def reduced_motion(self) -> bool:
        return self._reduced_motion

    def set_high_contrast(self, enabled: bool) -> None:
        if self._high_contrast == enabled:
            return
        self._high_contrast = enabled
        self.high_contrast_changed.emit(enabled)

    def toggle_high_contrast(self) -> None:
        self.set_high_contrast(not self._high_contrast)

    def set_reduced_motion(self, enabled: bool) -> None:
        if self._reduced_motion == enabled:
            return
        self._reduced_motion = enabled
        for w in self._reduced_motion_widgets:
            if hasattr(w, "set_reduced_motion"):
                w.set_reduced_motion(enabled)
        self.reduced_motion_changed.emit(enabled)

    def toggle_reduced_motion(self) -> None:
        self.set_reduced_motion(not self._reduced_motion)

    def register_reduced_motion_widget(self, widget: QWidget) -> None:
        if widget not in self._reduced_motion_widgets:
            self._reduced_motion_widgets.append(widget)
            if hasattr(widget, "set_reduced_motion"):
                widget.set_reduced_motion(self._reduced_motion)

    @staticmethod
    def set_accessible(
        widget: QWidget,
        name: str = "",
        description: str = "",
        tooltip: str = "",
    ) -> None:
        if name:
            widget.setAccessibleName(name)
        if description:
            widget.setAccessibleDescription(description)
        if tooltip:
            widget.setToolTip(tooltip)
