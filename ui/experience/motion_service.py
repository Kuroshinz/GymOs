from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import QEasingCurve, QEvent, QObject, QPoint, QPropertyAnimation, QRect, QTimer
from PySide6.QtWidgets import QFrame, QGraphicsOpacityEffect, QLabel, QPushButton, QWidget

from ui.design_system.tokens.shadow import apply_elevation, glow_effect
from ui.experience.accessibility import AccessibilityManager
from ui.experience.animation_manager import AnimationManager

_FADE_DURATION = 200
_STAGGER_DELAY = 80
_SLIDE_DISTANCE = 8
_PRESS_DURATION = 80
_HOVER_DURATION = 150
_COUNT_DURATION = 300


class _StaggerFadeSequence(QObject):
    def __init__(
        self,
        widgets: Sequence[QWidget],
        service: MotionService,
        stagger: int = _STAGGER_DELAY,
        slide: int = _SLIDE_DISTANCE,
        reduce: bool = False,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._index = 0
        self._widgets = widgets
        self._service = service
        self._stagger = stagger
        self._slide = slide
        self._reduce = reduce

    def start(self) -> None:
        if not self._widgets:
            return
        self._tick()

    def _tick(self) -> None:
        if self._index >= len(self._widgets):
            self.deleteLater()
            return
        w = self._widgets[self._index]
        if self._reduce:
            self._service._fade_in_widget(w, duration=100, easing=QEasingCurve.Type.OutCubic)
        else:
            self._service._fade_in_widget(w, duration=_FADE_DURATION, easing=QEasingCurve.Type.OutCubic)
            self._service._slide_up_widget(w, distance=self._slide, duration=_FADE_DURATION, easing=QEasingCurve.Type.OutCubic)
        self._index += 1
        QTimer.singleShot(self._stagger, self._tick)


class MotionService(QObject):
    def __init__(
        self,
        animation_manager: AnimationManager,
        accessibility: AccessibilityManager,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._anim = animation_manager
        self._access = accessibility
        self._active_hover: dict[int, bool] = {}
        self._active_anims: list[QPropertyAnimation] = []
        accessibility.reduced_motion_changed.connect(self._on_reduced_motion_changed)

    @property
    def reduced(self) -> bool:
        return self._access.reduced_motion

    def _on_reduced_motion_changed(self, enabled: bool) -> None:
        self.stop_all()

    def stop_all(self) -> None:
        self._anim.stop_all()

    # --- Fade in / out ---

    def _track(self, anim: QPropertyAnimation) -> None:
        self._active_anims.append(anim)
        anim.finished.connect(lambda: self._active_anims.remove(anim) if anim in self._active_anims else None)

    def _fade_in_widget(
        self,
        widget: QWidget,
        duration: int = _FADE_DURATION,
        easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic,
    ) -> None:
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(easing)
        anim.finished.connect(lambda: self._cleanup_opacity(widget, effect))
        self._track(anim)
        anim.start(QPropertyAnimation.DeleteWhenStopped)

    def _slide_up_widget(
        self,
        widget: QWidget,
        distance: int = _SLIDE_DISTANCE,
        duration: int = _FADE_DURATION,
        easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic,
    ) -> None:
        start_y = widget.pos().y() + distance
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setStartValue(QPoint(widget.pos().x(), start_y))
        anim.setEndValue(QPoint(widget.pos().x(), start_y - distance))
        anim.setEasingCurve(easing)
        self._track(anim)
        anim.start(QPropertyAnimation.DeleteWhenStopped)

    def _cleanup_opacity(self, widget: QWidget, effect: QGraphicsOpacityEffect) -> None:
        if widget.graphicsEffect() is effect:
            widget.setGraphicsEffect(None)

    # --- Public API ---

    def fade_in(
        self,
        widget: QWidget,
        duration: int = _FADE_DURATION,
        easing: QEasingCurve.Type = QEasingCurve.Type.OutCubic,
    ) -> None:
        if self.reduced:
            widget.setGraphicsEffect(None)
            return
        self._fade_in_widget(widget, duration, easing)

    def fade_out(
        self,
        widget: QWidget,
        duration: int = _FADE_DURATION,
        easing: QEasingCurve.Type = QEasingCurve.Type.InOutCubic,
        on_finished: Callable[[], None] | None = None,
    ) -> None:
        if self.reduced:
            if on_finished:
                on_finished()
            return
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(easing)
        if on_finished:

            def _done() -> None:
                self._cleanup_opacity(widget, effect)
                on_finished()

            anim.finished.connect(_done)
        else:
            anim.finished.connect(lambda: self._cleanup_opacity(widget, effect))
        self._track(anim)
        anim.start(QPropertyAnimation.DeleteWhenStopped)

    def fade_slide_in(
        self,
        widget: QWidget,
        duration: int = _FADE_DURATION,
        slide_distance: int = _SLIDE_DISTANCE,
    ) -> None:
        if self.reduced:
            widget.setGraphicsEffect(None)
            return
        self._fade_in_widget(widget, duration, QEasingCurve.Type.OutCubic)
        self._slide_up_widget(widget, slide_distance, duration, QEasingCurve.Type.OutCubic)

    def stagger_reveal(
        self,
        widgets: Sequence[QWidget],
        stagger: int = _STAGGER_DELAY,
        slide_distance: int = _SLIDE_DISTANCE,
    ) -> _StaggerFadeSequence:
        seq = _StaggerFadeSequence(widgets, self, stagger, slide_distance, self.reduced, self)
        seq.start()
        return seq

    # --- Sidebar ---

    def animate_width(
        self,
        widget: QWidget,
        target_width: int,
        duration: int = _FADE_DURATION,
    ) -> None:
        if self.reduced:
            widget.setFixedWidth(target_width)
            return
        anim = QPropertyAnimation(widget, b"minimumWidth")
        anim.setDuration(duration)
        anim.setStartValue(widget.width())
        anim.setEndValue(target_width)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._track(anim)
        anim.start(QPropertyAnimation.DeleteWhenStopped)

    # --- Page transition ---

    def transition_page(
        self,
        old_widget: QWidget | None,
        new_widget: QWidget,
        on_midpoint: Callable[[], None],
    ) -> None:
        if self.reduced or old_widget is None or old_widget is new_widget:
            on_midpoint()
            return

        def _mid() -> None:
            on_midpoint()
            self.fade_in(new_widget, duration=200)

        self.fade_out(old_widget, duration=150, easing=QEasingCurve.Type.InOutCubic, on_finished=_mid)

    # --- Hover ---

    def bind_hover_elevation(self, card: QWidget, raise_level: int = 1) -> None:
        orig_elevation = 0
        orig_glow = False
        card.setProperty("_motion_orig_elevation", orig_elevation)
        card.setProperty("_motion_orig_glow", orig_glow)
        card.installEventFilter(self)

    def eventFilter(self, obj: QObject, event) -> bool:
        if self.reduced:
            return super().eventFilter(obj, event)
        if isinstance(obj, QWidget):
            if event.type() == QEvent.Type.Enter:
                self._animate_hover(obj, enter=True)
            elif event.type() == QEvent.Type.Leave:
                self._animate_hover(obj, enter=False)
            elif event.type() == QEvent.Type.MouseButtonPress and isinstance(obj, QPushButton):
                self._animate_press(obj, pressed=True)
            elif event.type() == QEvent.Type.MouseButtonRelease and isinstance(obj, QPushButton):
                self._animate_press(obj, pressed=False)
        return super().eventFilter(obj, event)

    def _animate_hover(self, card: QWidget, enter: bool) -> None:
        h = id(card)
        if self._active_hover.get(h) == enter:
            return
        self._active_hover[h] = enter
        if enter:
            apply_elevation(card, level=1)
            glow_effect(card)
        else:
            apply_elevation(card, level=0)

    # --- Button press ---

    def bind_press_scale(self, button: QPushButton) -> None:
        button.installEventFilter(self)

    def _animate_press(self, button: QPushButton, pressed: bool) -> None:
        if self.reduced:
            return
        if pressed:
            geo = button.geometry()
            dw = int(geo.width() * 0.02)
            dh = int(geo.height() * 0.02)
            target = QRect(geo.x() + dw // 2, geo.y() + dh // 2, geo.width() - dw, geo.height() - dh)
            anim = QPropertyAnimation(button, b"geometry")
            anim.setDuration(_PRESS_DURATION)
            anim.setStartValue(geo)
            anim.setEndValue(target)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._track(anim)
            anim.start(QPropertyAnimation.DeleteWhenStopped)
        else:
            geo = button.geometry()
            dw = int(geo.width() * 0.02)
            dh = int(geo.height() * 0.02)
            start = QRect(geo.x() + dw // 2, geo.y() + dh // 2, geo.width() - dw, geo.height() - dh)
            anim = QPropertyAnimation(button, b"geometry")
            anim.setDuration(120)
            anim.setStartValue(start)
            anim.setEndValue(geo)
            anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._track(anim)
            anim.start(QPropertyAnimation.DeleteWhenStopped)

    # --- Count-up ---

    def count_up(
        self,
        label: QLabel,
        target_value: float,
        format_str: str = "{:.0f}",
        duration: int = _COUNT_DURATION,
    ) -> None:
        if self.reduced:
            label.setText(format_str.format(target_value))
            return
        self._animate_count(label, 0.0, target_value, format_str, duration)

    def _animate_count(self, label: QLabel, start: float, end: float, fmt: str, duration: int) -> None:
        steps = max(10, duration // 16)
        step = 0
        (end - start) / steps

        def _tick() -> None:
            nonlocal step
            step += 1
            progress = min(step / steps, 1.0)
            eased = 1.0 - (1.0 - progress) ** 3
            current = start + (end - start) * eased
            label.setText(fmt.format(current))
            if step < steps:
                QTimer.singleShot(16, _tick)

        QTimer.singleShot(16, _tick)

    # --- Chart draw ---

    def animate_progress_bar(self, bar: QFrame, target_width: int, duration: int = 250) -> None:
        if self.reduced:
            bar.setFixedWidth(target_width)
            return
        anim = QPropertyAnimation(bar, b"minimumWidth")
        anim.setDuration(duration)
        anim.setStartValue(0)
        anim.setEndValue(target_width)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._track(anim)
        anim.start(QPropertyAnimation.DeleteWhenStopped)

    def animate_chart_draw(self, canvas: QWidget, duration: int = 300) -> None:
        if self.reduced:
            return
        effect = QGraphicsOpacityEffect(canvas)
        canvas.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutQuart)
        anim.finished.connect(lambda: self._cleanup_opacity(canvas, effect))
        self._track(anim)
        anim.start(QPropertyAnimation.DeleteWhenStopped)
