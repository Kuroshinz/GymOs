from __future__ import annotations

import enum
from collections.abc import Callable

from PySide6.QtCore import QEasingCurve, QObject, QPoint, QPropertyAnimation, QSize, Signal
from PySide6.QtWidgets import QGraphicsOpacityEffect, QWidget


class AnimationType(enum.Enum):
    FADE = "fade"
    SLIDE = "slide"
    SCALE = "scale"
    BOUNCE = "bounce"
    PULSE = "pulse"


class AnimationPreset:
    DURATION_FAST = 150
    DURATION_NORMAL = 300
    DURATION_SLOW = 500
    EASE_IN_OUT = QEasingCurve.Type.InOutCubic
    EASE_OUT = QEasingCurve.Type.OutCubic
    EASE_IN = QEasingCurve.Type.InCubic


class SlideDirection(enum.Enum):
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"


class AnimationHandle:
    def __init__(self, animation: QPropertyAnimation) -> None:
        self._animation = animation
        self._finished = False
        animation.finished.connect(self._on_finished)

    def _on_finished(self) -> None:
        self._finished = True

    @property
    def is_running(self) -> bool:
        return self._animation.state() == QPropertyAnimation.State.Running

    @property
    def is_finished(self) -> bool:
        return self._finished

    def stop(self) -> None:
        self._animation.stop()

    def pause(self) -> None:
        self._animation.pause()

    def resume(self) -> None:
        self._animation.resume()


class AnimationManager(QObject):
    animation_started = Signal(str)
    animation_completed = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._handles: dict[str, AnimationHandle] = {}

    def fade_in(
        self,
        widget: QWidget,
        duration: int = AnimationPreset.DURATION_NORMAL,
        easing: QEasingCurve.Type = AnimationPreset.EASE_IN_OUT,
    ) -> AnimationHandle:
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(easing)
        anim.finished.connect(lambda: self._cleanup_fade(widget, effect))
        anim.start()
        handle = self._track("fade_in", anim)
        return handle

    def fade_out(
        self,
        widget: QWidget,
        duration: int = AnimationPreset.DURATION_NORMAL,
        easing: QEasingCurve.Type = AnimationPreset.EASE_IN_OUT,
        on_finished: Callable[[], None] | None = None,
    ) -> AnimationHandle:
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(easing)
        if on_finished:

            def _done() -> None:
                self._cleanup_fade(widget, effect)
                on_finished()

            anim.finished.connect(_done)
        else:
            anim.finished.connect(lambda: self._cleanup_fade(widget, effect))
        anim.start()
        handle = self._track("fade_out", anim)
        return handle

    @staticmethod
    def _cleanup_fade(widget: QWidget, effect: QGraphicsOpacityEffect) -> None:
        if widget.graphicsEffect() is effect:
            widget.setGraphicsEffect(None)

    def slide(
        self,
        widget: QWidget,
        direction: SlideDirection,
        distance: int = 20,
        duration: int = AnimationPreset.DURATION_NORMAL,
        easing: QEasingCurve.Type = AnimationPreset.EASE_OUT,
    ) -> AnimationHandle:
        start_pos = widget.pos()
        offset_map = {
            SlideDirection.LEFT: QPoint(-distance, 0),
            SlideDirection.RIGHT: QPoint(distance, 0),
            SlideDirection.UP: QPoint(0, -distance),
            SlideDirection.DOWN: QPoint(0, distance),
        }
        offset = offset_map[direction]
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setStartValue(QPoint(start_pos.x() + offset.x(), start_pos.y() + offset.y()))
        anim.setEndValue(start_pos)
        anim.setEasingCurve(easing)
        anim.start()
        handle = self._track(f"slide_{direction.value}", anim)
        return handle

    def scale(
        self,
        widget: QWidget,
        from_size: tuple[int, int],
        to_size: tuple[int, int],
        duration: int = AnimationPreset.DURATION_NORMAL,
        easing: QEasingCurve.Type = AnimationPreset.EASE_OUT,
    ) -> AnimationHandle:
        anim = QPropertyAnimation(widget, b"minimumSize")
        anim.setDuration(duration)
        anim.setStartValue(QSize(*from_size))
        anim.setEndValue(QSize(*to_size))
        anim.setEasingCurve(easing)
        anim.start()
        handle = self._track("scale", anim)
        return handle

    def bounce(
        self,
        widget: QWidget,
        distance: int = 5,
        duration: int = AnimationPreset.DURATION_FAST,
    ) -> AnimationHandle:
        start_pos = widget.pos()
        target_pos = QPoint(start_pos.x(), start_pos.y() - distance)
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setStartValue(start_pos)
        anim.setKeyValueAt(0.5, target_pos)
        anim.setEndValue(start_pos)
        anim.setEasingCurve(QEasingCurve.Type.OutBounce)
        anim.start()
        handle = self._track("bounce", anim)
        return handle

    def pulse(
        self,
        widget: QWidget,
        duration: int = AnimationPreset.DURATION_NORMAL,
    ) -> AnimationHandle:
        start_geo = widget.geometry()
        anim = QPropertyAnimation(widget, b"geometry")
        anim.setDuration(duration)
        anim.setLoopCount(2)
        mid_w = int(start_geo.width() * 1.02)
        mid_h = int(start_geo.height() * 1.02)
        mid_x = start_geo.center().x() - mid_w // 2
        mid_y = start_geo.center().y() - mid_h // 2
        anim.setStartValue(start_geo)
        anim.setKeyValueAt(0.5, start_geo.__class__(mid_x, mid_y, mid_w, mid_h))
        anim.setEndValue(start_geo)
        anim.setEasingCurve(QEasingCurve.Type.InOutSine)
        anim.start()
        handle = self._track("pulse", anim)
        return handle

    def stop_all(self) -> None:
        for handle in self._handles.values():
            handle.stop()
        self._handles.clear()

    def stop(self, key: str) -> None:
        handle = self._handles.get(key)
        if handle:
            handle.stop()
            del self._handles[key]

    def _track(self, key: str, anim: QPropertyAnimation) -> AnimationHandle:
        anim.deleteLater()
        handle = AnimationHandle(anim)
        anim.finished.connect(lambda: self._on_done(key))
        self._handles[key] = handle
        self.animation_started.emit(key)
        return handle

    def _on_done(self, key: str) -> None:
        self._handles.pop(key, None)
        self.animation_completed.emit(key)
