"""Motion System 2.0 — unified animation language for GymOS.

Every animation in the application is created through this module.
No page may invent its own QPropertyAnimation.
"""

from ui.design_system.motion.animation_factory import AnimationFactory
from ui.design_system.motion.motion_accessibility import MotionAccessibility
from ui.design_system.motion.motion_manager import MotionManager
from ui.design_system.motion.motion_presets import MotionPresets
from ui.design_system.motion.motion_tokens import (
    CurveTokens,
    DurationTokens,
    MotionTokens,
    StaggerTokens,
)
from ui.design_system.motion.transition_manager import TransitionManager

__all__ = [
    "MotionTokens",
    "DurationTokens",
    "CurveTokens",
    "StaggerTokens",
    "AnimationFactory",
    "MotionManager",
    "MotionPresets",
    "MotionAccessibility",
    "TransitionManager",
]
