from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.plugin import Plugin as CorePlugin, PluginManifest


@dataclass
class PluginConfig:
    enabled: bool = True
    settings: dict[str, Any] = field(default_factory=dict)
    credentials: dict[str, str] = field(default_factory=dict)


class Plugin(CorePlugin):
    """Base class for all NEXUS plugins.

    Usage:
        class MyPlugin(Plugin):
            manifest = PluginManifest(
                name="my_plugin",
                version="1.0.0",
                description="...",
                author="...",
                requires_capabilities=["network.http"],
            )

            async def on_load(self) -> None:
                # Access event bus via nexus.platform.event_bus
                self.event_bus.on("workout.created", self.on_workout)

            async def on_unload(self) -> None:
                ...

            async def on_workout(self, event):
                ...

    Plugin authors should NOT import from core directly.
    Use the SDK exports instead.
    """

    def __init__(self) -> None:
        super().__init__()
        self.config: PluginConfig = PluginConfig()


__all__ = ["Plugin", "PluginManifest", "PluginConfig"]
