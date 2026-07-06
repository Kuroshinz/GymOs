from __future__ import annotations

import logging
from typing import Any

from ui.command_center.theme import PAGE_LABELS
from ui.experience.experience_manager import ExperienceManager

logger = logging.getLogger("experience.integration")


def integrate_with_command_center(
    experience: ExperienceManager,
    command_center_data_provider: Any = None,
) -> None:
    if command_center_data_provider:
        try:
            experience.propagate_data(command_center_data_provider)
        except Exception:
            pass

    experience.register_default_page_routes(PAGE_LABELS)
    experience.register_default_command_palette_pages(PAGE_LABELS)

    logger.info(
        "Experience Platform integrated with Command Center (%d routes, %d commands)",
        len(experience.navigation.all_routes),
        experience.command_palette.count,
    )
