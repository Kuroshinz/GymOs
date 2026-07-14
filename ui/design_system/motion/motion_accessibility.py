"""Motion accessibility — centralized reduced-motion support.

Wraps AccessibilityManager and provides a consistent API for all motion
components. Every animation in the application checks this before running.
"""

from __future__ import annotations

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget


class MotionAccessibility(QObject):
    """Reduced motion controller.

    One switch. Everything respects it. No exceptions.

    Usage:
        from ui.design_system.motion import MotionAccessibility
        a11y = MotionAccessibility(existing_accessibility_manager)
        if a11y.reduced:
            return  # skip animation
    """

    reduced_motion_changed = Signal(bool)

    def __init__(
        self,
        existing_accessibility=None,
        parent: QObject | None = None,
    ) -> None:
        """Wrap an existing AccessibilityManager or create standalone."""
        super().__init__(parent)
        self._external = existing_accessibility
        self._reduced = False
        self._registered_widgets: list[QWidget] = []

        if existing_accessibility is not None:
            self._reduced = getattr(existing_accessibility, 'reduced_motion', False)
            existing_accessibility.reduced_motion_changed.connect(self._sync)

    @property
    def reduced(self) -> bool:
        """True when reduced motion is enabled. All animations should skip."""
        return self._reduced

    def _sync(self, enabled: bool) -> None:
        """Sync with external AccessibilityManager."""
        if self._reduced == enabled:
            return
        self._reduced = enabled
        for w in self._registered_widgets:
            if hasattr(w, 'set_reduced_motion'):
                w.set_reduced_motion(enabled)
        self.reduced_motion_changed.emit(enabled)

    def register(self, widget: QWidget) -> None:
        """Register a widget that supports set_reduced_motion()."""
        if widget not in self._registered_widgets:
            self._registered_widgets.append(widget)
            if hasattr(widget, 'set_reduced_motion'):
                widget.set_reduced_motion(self._reduced)

    def unregister(self, widget: QWidget) -> None:
        """Remove a widget from reduced-motion tracking."""
        if widget in self._registered_widgets:
            self._registered_widgets.remove(widget)

    def set_reduced(self, enabled: bool) -> None:
        """Programmatically enable/disable reduced motion."""
        if self._external is not None:
            if hasattr(self._external, 'set_reduced_motion'):
                self._external.set_reduced_motion(enabled)
            return
        self._sync(enabled)
