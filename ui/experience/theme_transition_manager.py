from __future__ import annotations

import logging
from typing import Any

from PySide6.QtCore import QEasingCurve, QObject, QPropertyAnimation, Signal
from PySide6.QtWidgets import QWidget

from ui.command_center.theme import C
from ui.experience.animation_manager import AnimationManager, AnimationPreset

logger = logging.getLogger("experience.theme_transition")


class ThemeTransitionManager(QObject):
    transition_started = Signal(str, str)
    transition_completed = Signal(str, str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._animation: AnimationManager | None = None
        self._transition_duration = AnimationPreset.DURATION_SLOW
        self._widgets: list[QWidget] = []

    def set_animation_manager(self, animation: AnimationManager) -> None:
        self._animation = animation

    def register_widget(self, widget: QWidget) -> None:
        if widget not in self._widgets:
            self._widgets.append(widget)

    def unregister_widget(self, widget: QWidget) -> None:
        if widget in self._widgets:
            self._widgets.remove(widget)

    def transition_to(self, theme_name: str, duration: int | None = None) -> None:
        prev_theme = "current"
        self.transition_started.emit(prev_theme, theme_name)

        actual_duration = duration or self._transition_duration

        try:
            from core.theme import ThemeManager
            manager = ThemeManager()
            manager.activate(theme_name)
        except Exception:
            logger.warning("Theme '%s' not available, skipping transition", theme_name)
            return

        for widget in self._widgets:
            try:
                widget.setStyleSheet(self._theme_styleheet())
            except Exception:
                pass

        if self._animation:
            for widget in self._widgets:
                try:
                    self._animation.fade_out(widget, duration=actual_duration // 2, easing=QEasingCurve.Type.OutCubic)
                except Exception:
                    pass

        self.transition_completed.emit(prev_theme, theme_name)

    def animate_style_change(
        self,
        widget: QWidget,
        property_name: bytes,
        start_value: Any,
        end_value: Any,
        duration: int | None = None,
    ) -> None:
        anim = QPropertyAnimation(widget, property_name)
        anim.setDuration(duration or self._transition_duration)
        anim.setStartValue(start_value)
        anim.setEndValue(end_value)
        anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        anim.start()

    def fade_to_theme(self, theme_name: str, duration: int = 500) -> None:
        if self._animation:
            for widget in self._widgets:
                self._animation.fade_out(widget, duration=duration // 2)

        try:
            from core.theme import ThemeManager
            manager = ThemeManager()
            manager.activate(theme_name)
        except Exception:
            logger.warning("Theme '%s' not found", theme_name)

        for widget in self._widgets:
            try:
                widget.setStyleSheet(self._theme_styleheet())
            except Exception:
                pass

        if self._animation:
            for widget in self._widgets:
                self._animation.fade_in(widget, duration=duration // 2)

        self.transition_completed.emit("previous", theme_name)

    def set_duration(self, ms: int) -> None:
        self._transition_duration = ms

    @property
    def duration(self) -> int:
        return self._transition_duration

    def _theme_styleheet(self) -> str:
        return f"""
            QWidget {{
                background-color: {C.BG};
                color: {C.TEXT_PRIMARY};
            }}
        """
