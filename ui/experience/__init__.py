from __future__ import annotations

from ui.experience.accessibility import AccessibilityManager
from ui.experience.experience_manager import ExperienceManager
from ui.experience.motion_service import MotionService


def create_experience_platform(parent=None):
    return ExperienceManager(parent)


__all__ = ["create_experience_platform", "ExperienceManager", "AccessibilityManager", "MotionService"]
