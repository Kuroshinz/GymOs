from __future__ import annotations

from ui.experience.experience_manager import ExperienceManager


def create_experience_platform(parent=None):
    return ExperienceManager(parent)


__all__ = ["create_experience_platform", "ExperienceManager"]
