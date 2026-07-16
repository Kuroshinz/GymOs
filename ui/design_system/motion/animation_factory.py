"""Animation factory — creates configured QPropertyAnimation objects from tokens.

Stateless. Every method returns a ready-to-start QPropertyAnimation.
No side effects. No state.
"""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPoint, QPropertyAnimation, QRect, QSize
from PySide6.QtWidgets import QGraphicsOpacityEffect, QWidget

from ui.design_system.motion.motion_tokens import MotionTokens

MT = MotionTokens()


class AnimationFactory:
    """Stateless factory for creating QPropertyAnimation objects from tokens."""

    # ── Opacity ───────────────────────────────────────────────────

    @staticmethod
    def fade_in(
        widget: QWidget,
        duration: int = MT.normal,
        easing: QEasingCurve.Type = MT.out_cubic,
    ) -> QPropertyAnimation:
        """Create a fade-in animation (opacity 0 → 1)."""
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(easing)
        return anim

    @staticmethod
    def safe_fade_in(
        widget: QWidget,
        duration: int = MT.normal,
        easing: QEasingCurve.Type = MT.out_cubic,
    ) -> QPropertyAnimation | None:
        """Create a fade-in animation, respecting reduced-motion preferences."""
        window = widget.window()
        reduced_motion = False
        if window:
            experience = getattr(window, "_experience", None)
            if experience and hasattr(experience, "accessibility"):
                reduced_motion = experience.accessibility.reduced_motion
        
        if reduced_motion:
            effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(effect)
            effect.setOpacity(1.0)
            return None
            
        return AnimationFactory.fade_in(widget, duration, easing)

    @staticmethod
    def fade_out(
        widget: QWidget,
        duration: int = MT.normal,
        easing: QEasingCurve.Type = MT.in_out_cubic,
    ) -> QPropertyAnimation:
        """Create a fade-out animation (opacity 1 → 0)."""
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(easing)
        return anim

    @staticmethod
    def cleanup_opacity(widget: QWidget) -> None:
        """Remove the opacity effect from a widget after fade animation completes."""
        effect = widget.graphicsEffect()
        if isinstance(effect, QGraphicsOpacityEffect):
            widget.setGraphicsEffect(None)

    # ── Position ──────────────────────────────────────────────────

    @staticmethod
    def slide_up(
        widget: QWidget,
        distance: int = 8,
        duration: int = MT.normal,
        easing: QEasingCurve.Type = MT.out_cubic,
    ) -> QPropertyAnimation:
        """Create a slide-up animation."""
        start_y = widget.pos().y() + distance
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setStartValue(QPoint(widget.pos().x(), start_y))
        anim.setEndValue(QPoint(widget.pos().x(), start_y - distance))
        anim.setEasingCurve(easing)
        return anim

    @staticmethod
    def slide_down(
        widget: QWidget,
        distance: int = 8,
        duration: int = MT.normal,
        easing: QEasingCurve.Type = MT.out_cubic,
    ) -> QPropertyAnimation:
        """Create a slide-down animation."""
        start_y = widget.pos().y() - distance
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setStartValue(QPoint(widget.pos().x(), start_y))
        anim.setEndValue(QPoint(widget.pos().x(), start_y + distance))
        anim.setEasingCurve(easing)
        return anim

    @staticmethod
    def slide_left(
        widget: QWidget,
        distance: int = 20,
        duration: int = MT.normal,
        easing: QEasingCurve.Type = MT.out_cubic,
    ) -> QPropertyAnimation:
        """Create a slide-left animation."""
        start_x = widget.pos().x() + distance
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setStartValue(QPoint(start_x, widget.pos().y()))
        anim.setEndValue(QPoint(start_x - distance, widget.pos().y()))
        anim.setEasingCurve(easing)
        return anim

    @staticmethod
    def slide_right(
        widget: QWidget,
        distance: int = 20,
        duration: int = MT.normal,
        easing: QEasingCurve.Type = MT.out_cubic,
    ) -> QPropertyAnimation:
        """Create a slide-right animation (e.g., toast enter)."""
        start_x = widget.pos().x() - distance
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(duration)
        anim.setStartValue(QPoint(start_x, widget.pos().y()))
        anim.setEndValue(QPoint(start_x + distance, widget.pos().y()))
        anim.setEasingCurve(easing)
        return anim

    # ── Size ──────────────────────────────────────────────────────

    @staticmethod
    def animate_width(
        widget: QWidget,
        target_width: int,
        duration: int = MT.normal,
        easing: QEasingCurve.Type = MT.out_cubic,
    ) -> QPropertyAnimation:
        """Create a width animation (e.g., sidebar expand/collapse)."""
        anim = QPropertyAnimation(widget, b"minimumWidth")
        anim.setDuration(duration)
        anim.setStartValue(widget.width())
        anim.setEndValue(target_width)
        anim.setEasingCurve(easing)
        return anim

    @staticmethod
    def animate_size(
        widget: QWidget,
        from_size: tuple[int, int],
        to_size: tuple[int, int],
        duration: int = MT.normal,
        easing: QEasingCurve.Type = MT.out_cubic,
    ) -> QPropertyAnimation:
        """Create a size animation (scale effect)."""
        anim = QPropertyAnimation(widget, b"minimumSize")
        anim.setDuration(duration)
        anim.setStartValue(QSize(*from_size))
        anim.setEndValue(QSize(*to_size))
        anim.setEasingCurve(easing)
        return anim

    # ── Geometry ──────────────────────────────────────────────────

    @staticmethod
    def animate_geometry(
        widget: QWidget,
        start_rect: QRect,
        end_rect: QRect,
        duration: int = MT.normal,
        easing: QEasingCurve.Type = MT.out_cubic,
    ) -> QPropertyAnimation:
        """Create a geometry animation (e.g., button press)."""
        anim = QPropertyAnimation(widget, b"geometry")
        anim.setDuration(duration)
        anim.setStartValue(start_rect)
        anim.setEndValue(end_rect)
        anim.setEasingCurve(easing)
        return anim

    # ── Progress Bar ──────────────────────────────────────────────

    @staticmethod
    def fill_bar(
        widget: QWidget,
        target_width: int,
        duration: int = MT.slow,
        easing: QEasingCurve.Type = MT.out_cubic,
    ) -> QPropertyAnimation:
        """Create a progress bar fill animation."""
        anim = QPropertyAnimation(widget, b"minimumWidth")
        anim.setDuration(duration)
        anim.setStartValue(0)
        anim.setEndValue(target_width)
        anim.setEasingCurve(easing)
        return anim
