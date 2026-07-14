"""Transition manager — page-level transition orchestration.

Handles crossfade between pages during navigation.
Supports custom on_midpoint callbacks for swapping page content.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QWidget

from ui.design_system.motion.motion_accessibility import MotionAccessibility
from ui.design_system.motion.motion_manager import MotionManager
from ui.design_system.motion.motion_tokens import MotionTokens

MT = MotionTokens()


class TransitionManager(QObject):
    """Page transition orchestrator.

    Provides a simple API for page-level transitions:
        tm = TransitionManager(motion_manager)
        tm.crossfade(current_page, next_page, on_swap)
    """

    def __init__(
        self,
        motion: MotionManager,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._motion = motion

    @property
    def reduced(self) -> bool:
        return self._motion.reduced

    def crossfade(
        self,
        old_page: QWidget | None,
        new_page: QWidget,
        on_swap: Callable[[], None],
    ) -> None:
        """Crossfade transition: fade out old → swap → fade in new.

        Duration: ~350ms total (150ms out + 200ms in).
        """
        self._motion.transition_page(old_page, new_page, on_swap)

    def replace_instant(
        self,
        old_page: QWidget | None,
        new_page: QWidget,
        on_swap: Callable[[], None],
    ) -> None:
        """Instant page replacement with no animation. For reduced motion."""
        on_swap()

    def fade_in_new(self, new_page: QWidget) -> None:
        """Fade in a new page without fading out the old one."""
        self._motion.fade_in(new_page, duration=MT.normal)
