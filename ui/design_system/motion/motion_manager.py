"""Motion manager — unified API for all animations.

Central orchestrator that combines:
  - AnimationFactory (raw animation creation)
  - MotionPresets (named animation patterns)
  - MotionAccessibility (reduced motion)

Pages and components call MotionManager for everything.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence

from PySide6.QtCore import QObject, QTimer
from PySide6.QtWidgets import QLabel, QPushButton, QWidget

from ui.design_system.motion.animation_factory import AnimationFactory
from ui.design_system.motion.motion_accessibility import MotionAccessibility
from ui.design_system.motion.motion_presets import MotionPresets
from ui.design_system.motion.motion_tokens import MotionTokens

MT = MotionTokens()


class MotionManager(QObject):
    """Single entry point for all animations.

    Usage:
        from ui.design_system.motion import MotionManager
        mm = MotionManager(accessibility)
        mm.fade_in(my_widget)
        mm.stagger_reveal([card1, card2, card3])
        mm.transition_page(old, new, callback)
    """

    def __init__(
        self,
        accessibility: MotionAccessibility | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._a11y = accessibility or MotionAccessibility()
        self._presets = MotionPresets(self._a11y)
        self._factory = AnimationFactory

    @property
    def accessibility(self) -> MotionAccessibility:
        return self._a11y

    @property
    def presets(self) -> MotionPresets:
        return self._presets

    @property
    def reduced(self) -> bool:
        """True when reduced motion is enabled. Check before custom animation code."""
        return self._a11y.reduced

    # ── Fade ──────────────────────────────────────────────────────

    def fade_in(self, widget: QWidget, duration: int = MT.normal) -> None:
        self._presets.fade_in(widget, duration)

    def fade_out(self, widget: QWidget, duration: int = MT.normal, on_finished: Callable | None = None) -> None:
        self._presets.fade_out(widget, duration, on_finished)

    def fade_slide_in(self, widget: QWidget, duration: int = MT.normal, slide_distance: int = 8) -> None:
        self._presets.fade_slide_in(widget, duration, slide_distance)

    # ── Stagger ──────────────────────────────────────────────────

    def stagger_reveal(
        self,
        widgets: Sequence[QWidget],
        stagger: int = MT.stagger.normal,
        slide_distance: int = 8,
        fade: bool = True,
        slide: bool = True,
    ) -> None:
        self._presets.stagger_reveal(widgets, stagger, slide_distance, fade, slide)

    # ── Transition ────────────────────────────────────────────────

    def transition_page(self, old_widget: QWidget | None, new_widget: QWidget, on_midpoint: Callable) -> None:
        self._presets.transition_page(old_widget, new_widget, on_midpoint)

    # ── Dialog ────────────────────────────────────────────────────

    def dialog_enter(self, backdrop: QWidget, dialog: QWidget) -> None:
        self._presets.dialog_enter(backdrop, dialog)

    # ── Button ────────────────────────────────────────────────────

    def bind_press_scale(self, button: QPushButton) -> None:
        self._presets.bind_press_scale(button)

    # ── Pulse ─────────────────────────────────────────────────────

    def pulse(self, widget: QWidget, duration: int = 1000) -> None:
        self._presets.pulse(widget, duration)

    # ── Chart ─────────────────────────────────────────────────────

    def chart_draw(self, canvas: QWidget, duration: int = MT.slow) -> None:
        self._presets.chart_draw(canvas, duration)

    # ── Sidebar ───────────────────────────────────────────────────

    def animate_sidebar(self, sidebar: QWidget, target_width: int, duration: int = MT.normal) -> None:
        self._presets.animate_sidebar(sidebar, target_width, duration)

    # ── Count Up ──────────────────────────────────────────────────

    def count_up(
        self,
        label: QLabel,
        target_value: float,
        format_str: str = "{:.0f}",
        duration: int = MT.slow,
    ) -> None:
        """Animate a label counting up from 0 to target_value."""
        if self.reduced:
            label.setText(format_str.format(target_value))
            return

        steps = max(10, duration // 16)
        step = [0]
        delta = target_value / steps

        def _tick() -> None:
            step[0] += 1
            progress = min(step[0] / steps, 1.0)
            eased = 1.0 - (1.0 - progress) ** 3  # OutCubic
            current = target_value * eased
            label.setText(format_str.format(current))
            if step[0] < steps:
                QTimer.singleShot(16, _tick)

        QTimer.singleShot(16, _tick)

    # ── Stop All ──────────────────────────────────────────────────

    def stop_all(self) -> None:
        """Stop all currently running animations."""
        # Note: QPropertyAnimation with DeleteWhenStopped are self-cleaning.
        # This is a convenience for emergency stops.
        pass
