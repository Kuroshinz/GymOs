"""Motion presets — high-level named animation patterns.

Each preset combines one or more AnimationFactory calls into a
ready-to-use pattern. Pages call presets, not raw factories.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, QTimer
from PySide6.QtWidgets import QGraphicsOpacityEffect, QPushButton, QWidget

from ui.design_system.motion.animation_factory import AnimationFactory
from ui.design_system.motion.motion_accessibility import MotionAccessibility
from ui.design_system.motion.motion_tokens import MotionTokens

MT = MotionTokens()


class _StaggerSequence(QObject):
    """Internal stagger reveal sequence manager."""

    def __init__(
        self,
        widgets: Sequence[QWidget],
        factory: type[AnimationFactory],
        accessibility: MotionAccessibility | None,
        stagger: int,
        slide_distance: int,
        fade: bool,
        slide: bool,
    ) -> None:
        super().__init__()
        self._widgets = list(widgets)
        self._factory = factory
        self._accessibility = accessibility
        self._stagger = stagger
        self._slide_distance = slide_distance
        self._fade = fade
        self._slide = slide
        self._index = 0

    def start(self) -> None:
        if not self._widgets:
            self.deleteLater()
            return
        if self._accessibility and self._accessibility.reduced:
            self.deleteLater()
            return
        self._tick()

    def _tick(self) -> None:
        if self._index >= len(self._widgets):
            self.deleteLater()
            return
        w = self._widgets[self._index]
        anims = []
        if self._fade:
            a = self._factory.fade_in(w, duration=MT.normal)
            anims.append(a)
        if self._slide:
            a = self._factory.slide_up(w, distance=self._slide_distance, duration=MT.normal)
            anims.append(a)
        for a in anims:
            a.finished.connect(lambda captured_w=w: self._factory.cleanup_opacity(captured_w))
            a.start(QPropertyAnimation.DeleteWhenStopped)
        self._index += 1
        QTimer.singleShot(self._stagger, self._tick)


class MotionPresets(QObject):
    """High-level animation presets.

    Every preset checks MotionAccessibility before running.
    If reduced motion is enabled, presets skip immediately.
    """

    def __init__(self, accessibility: MotionAccessibility | None = None) -> None:
        self._factory = AnimationFactory
        self._a11y = accessibility

    @property
    def _skip(self) -> bool:
        return self._a11y is not None and self._a11y.reduced

    # ── Basic Presets ────────────────────────────────────────────

    def fade_in(self, widget: QWidget, duration: int = MT.normal) -> None:
        """Fade a widget in. The most common animation."""
        if self._skip:
            return
        anim = self._factory.fade_in(widget, duration)
        anim.finished.connect(lambda: self._factory.cleanup_opacity(widget))
        anim.start(QPropertyAnimation.DeleteWhenStopped)

    def fade_out(self, widget: QWidget, duration: int = MT.normal, on_finished: Callable | None = None) -> None:
        """Fade a widget out."""
        if self._skip:
            if on_finished:
                on_finished()
            return
        anim = self._factory.fade_out(widget, duration)
        if on_finished:
            def _done() -> None:
                self._factory.cleanup_opacity(widget)
                on_finished()
            anim.finished.connect(_done)
        else:
            anim.finished.connect(lambda: self._factory.cleanup_opacity(widget))
        anim.start(QPropertyAnimation.DeleteWhenStopped)

    def fade_slide_in(self, widget: QWidget, duration: int = MT.normal, slide_distance: int = 8) -> None:
        """Fade in + slide up simultaneously. Standard card reveal."""
        if self._skip:
            return
        anim = self._factory.fade_in(widget, duration)
        anim.finished.connect(lambda: self._factory.cleanup_opacity(widget))
        anim.start(QPropertyAnimation.DeleteWhenStopped)
        anim2 = self._factory.slide_up(widget, slide_distance, duration)
        anim2.start(QPropertyAnimation.DeleteWhenStopped)

    def slide_in_from_right(self, widget: QWidget, duration: int = MT.normal) -> None:
        """Slide in from the right (toast enter)."""
        if self._skip:
            return
        anim = self._factory.slide_right(widget, duration=duration)
        anim.start(QPropertyAnimation.DeleteWhenStopped)

    # ── Stagger ──────────────────────────────────────────────────

    def stagger_reveal(
        self,
        widgets: Sequence[QWidget],
        stagger: int = MT.stagger.normal,
        slide_distance: int = 8,
        fade: bool = True,
        slide: bool = True,
    ) -> _StaggerSequence:
        """Sequentially reveal widgets with stagger delay.

        Args:
            widgets: Widgets to reveal in order
            stagger: Delay between each widget (ms)
            slide_distance: Slide distance in pixels
            fade: Whether to fade in
            slide: Whether to slide up
        """
        seq = _StaggerSequence(widgets, self._factory, self._a11y, stagger, slide_distance, fade, slide)
        seq.start()
        return seq

    # ── Page Transition ──────────────────────────────────────────

    def transition_page(self, old_widget: QWidget | None, new_widget: QWidget, on_midpoint: Callable) -> None:
        """Crossfade page transition: fade out old → midpoint callback → fade in new.

        Duration: 150ms fade out + 200ms fade in = 350ms total.
        """
        if self._skip or old_widget is None or old_widget is new_widget:
            on_midpoint()
            return

        def _mid() -> None:
            on_midpoint()
            self.fade_in(new_widget, duration=200)

        self.fade_out(old_widget, duration=150, on_finished=_mid)

    # ── Dialog ───────────────────────────────────────────────────

    def dialog_enter(self, backdrop: QWidget, dialog: QWidget) -> None:
        """Dialog entrance: backdrop fade + dialog scale (0.96→1.0)."""
        if self._skip:
            return
        # Backdrop fade
        anim = self._factory.fade_in(backdrop, duration=MT.normal, easing=QEasingCurve.Type.Linear)
        anim.finished.connect(lambda: self._factory.cleanup_opacity(backdrop))
        anim.start(QPropertyAnimation.DeleteWhenStopped)

        # Dialog scale (simulate with geometry)
        start_geo = dialog.geometry()
        mid_w = int(start_geo.width() * 0.96)
        mid_h = int(start_geo.height() * 0.96)
        mid_x = start_geo.center().x() - mid_w // 2
        mid_y = start_geo.center().y() - mid_h // 2
        end_geo = start_geo
        start_scale = QRect(mid_x, mid_y, mid_w, mid_h)

        anim2 = self._factory.animate_geometry(dialog, start_scale, end_geo, duration=MT.normal)
        anim2.start(QPropertyAnimation.DeleteWhenStopped)

    # ── Button ────────────────────────────────────────────────────

    def bind_press_scale(self, button: QPushButton) -> None:
        """Bind press-scale (0.98) to a button via event filter.

        Call this once during setup. The button will animate on press/release.
        """
        if self._skip:
            return
        button.installEventFilter(self)

    def eventFilter(self, obj, event) -> bool:  # noqa: N802
        if self._skip or not isinstance(obj, QPushButton):
            return super().eventFilter(obj, event)

        if event.type() == event.Type.MouseButtonPress:
            self._press(obj)
        elif event.type() == event.Type.MouseButtonRelease:
            self._release(obj)

        return super().eventFilter(obj, event)

    def _press(self, button: QPushButton) -> None:
        geo = button.geometry()
        dw = int(geo.width() * 0.02)
        dh = int(geo.height() * 0.02)
        target = QRect(geo.x() + dw // 2, geo.y() + dh // 2, geo.width() - dw, geo.height() - dh)
        anim = self._factory.animate_geometry(button, geo, target, duration=MT.instant)
        anim.start(QPropertyAnimation.DeleteWhenStopped)

    def _release(self, button: QPushButton) -> None:
        geo = button.geometry()
        dw = int(geo.width() * 0.02)
        dh = int(geo.height() * 0.02)
        start = QRect(geo.x() + dw // 2, geo.y() + dh // 2, geo.width() - dw, geo.height() - dh)
        anim = self._factory.animate_geometry(button, start, geo, duration=MT.fast)
        anim.start(QPropertyAnimation.DeleteWhenStopped)

    # ── Pulse ─────────────────────────────────────────────────────

    def pulse(self, widget: QWidget, duration: int = 1000) -> None:
        """Gentle pulse animation (1.0 → 1.02 → 1.0)."""
        if self._skip:
            return
        start_geo = widget.geometry()
        mid_w = int(start_geo.width() * 1.02)
        mid_h = int(start_geo.height() * 1.02)
        mid_x = start_geo.center().x() - mid_w // 2
        mid_y = start_geo.center().y() - mid_h // 2

        anim = self._factory.animate_geometry(widget, start_geo, start_geo, duration, easing=QEasingCurve.Type.InOutSine)
        anim.setLoopCount(2)
        anim.setKeyValueAt(0.5, QRect(mid_x, mid_y, mid_w, mid_h))
        anim.setEndValue(start_geo)
        anim.start(QPropertyAnimation.DeleteWhenStopped)

    # ── Chart ─────────────────────────────────────────────────────

    def chart_draw(self, canvas: QWidget, duration: int = MT.slow) -> None:
        """Progressive chart draw via opacity fade."""
        if self._skip:
            return
        anim = self._factory.fade_in(canvas, duration, easing=QEasingCurve.Type.OutQuart)
        anim.finished.connect(lambda: self._factory.cleanup_opacity(canvas))
        anim.start(QPropertyAnimation.DeleteWhenStopped)

    # ── Sidebar ───────────────────────────────────────────────────

    def animate_sidebar(self, sidebar: QWidget, target_width: int, duration: int = MT.normal) -> None:
        """Smooth sidebar expand/collapse."""
        if self._skip:
            sidebar.setFixedWidth(target_width)
            return
        anim = self._factory.animate_width(sidebar, target_width, duration)
        anim.start(QPropertyAnimation.DeleteWhenStopped)
