"""Motion tokens — single source of truth for animation timing and curves.

These are the ONLY source of duration and curve values for all animations.
No magic numbers in any page.
"""

from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QEasingCurve


@dataclass(frozen=True)
class DurationTokens:
    """Animation durations in milliseconds.

    Every duration communicates a specific level of importance:
      instant  (80ms)  — Feedback (button press, hover)
      fast     (140ms) — Confirmation (badge, toast)
      normal   (220ms) — Standard reveal (card, section)
      slow     (320ms) — Emphasis (hero, state change)
      hero     (450ms) — Celebration (achievement, milestone)
    """
    instant: int = 80
    fast: int = 140
    normal: int = 220
    slow: int = 320
    hero: int = 450


@dataclass(frozen=True)
class CurveTokens:
    """Easing curve types for QPropertyAnimation.

    Each curve communicates a specific feeling:
      OutCubic    — Natural, calm (default for most UI)
      InOutCubic  — Professional, deliberate (page transitions)
      OutQuart    — Pronounced, premium (heroes, achievements)
      OutBounce   — Playful, energetic (feedback)
      OutQuad     — Gentle (hover effects)
      InOutSine   — Smooth (pulse, breathing)
      Linear      — Mechanical (progress bars, countdowns)
    """
    linear: QEasingCurve.Type = QEasingCurve.Type.Linear
    out_quad: QEasingCurve.Type = QEasingCurve.Type.OutQuad
    out_cubic: QEasingCurve.Type = QEasingCurve.Type.OutCubic
    in_out_cubic: QEasingCurve.Type = QEasingCurve.Type.InOutCubic
    out_quart: QEasingCurve.Type = QEasingCurve.Type.OutQuart
    out_quint: QEasingCurve.Type = QEasingCurve.Type.OutQuint
    out_bounce: QEasingCurve.Type = QEasingCurve.Type.OutBounce
    in_out_sine: QEasingCurve.Type = QEasingCurve.Type.InOutSine


@dataclass(frozen=True)
class StaggerTokens:
    """Stagger delays for sequential reveal animations.

      fast   (40ms)  — Dense lists (4+ items)
      normal (60ms)  — Card grids (3-4 items)
      slow   (100ms) — Hero sections (1-2 items)
    """
    fast: int = 40
    normal: int = 60
    slow: int = 100


@dataclass(frozen=True)
class MotionTokens:
    """Complete motion token collection.

    Usage:
        from ui.design_system.motion import MotionTokens
        MT = MotionTokens()
        anim.setDuration(MT.duration.normal)
        anim.setEasingCurve(MT.curve.out_cubic)
    """
    duration: DurationTokens = DurationTokens()
    curve: CurveTokens = CurveTokens()
    stagger: StaggerTokens = StaggerTokens()

    # Convenience shortcuts
    @property
    def instant(self) -> int:
        return self.duration.instant

    @property
    def fast(self) -> int:
        return self.duration.fast

    @property
    def normal(self) -> int:
        return self.duration.normal

    @property
    def slow(self) -> int:
        return self.duration.slow

    @property
    def hero(self) -> int:
        return self.duration.hero

    @property
    def out_cubic(self) -> QEasingCurve.Type:
        return self.curve.out_cubic

    @property
    def in_out_cubic(self) -> QEasingCurve.Type:
        return self.curve.in_out_cubic

    @property
    def out_quart(self) -> QEasingCurve.Type:
        return self.curve.out_quart

    @property
    def linear(self) -> QEasingCurve.Type:
        return self.curve.linear
