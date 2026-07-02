from __future__ import annotations

import logging
from typing import Optional

from core.config import Config
from core.di import Container, ServiceLifetime
from core.event_bus import EventBus
from core.logger import Logger
from core.cache import Cache
from core.scheduler import Scheduler
from core.notification import NotificationService
from core.theme import ThemeManager
from core.security import SecurityManager
from core.plugin import PluginManager
from core.command import CommandBus
from core.settings import SettingsManager

logger = logging.getLogger("nexus.platform")


class Platform:
    _instance: Optional["Platform"] = None

    def __new__(cls) -> "Platform":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self.container = Container()
        self.event_bus = EventBus()
        self.logger = Logger()
        self.config = Config()
        self.cache = Cache()
        self.scheduler = Scheduler()
        self.notifications = NotificationService()
        self.theme = ThemeManager()
        self.security = SecurityManager()
        self.plugins = PluginManager()
        self.commands = CommandBus()
        self.settings = SettingsManager()
        self._initialized = False

    def bootstrap(self) -> None:
        if self._initialized:
            return

        self.logger.setup()
        self.logger.info("Initializing NEXUS Platform...")

        svc = self.container
        svc.register("config", self.config)
        svc.register("event_bus", self.event_bus)
        svc.register("logger", self.logger)
        svc.register("cache", self.cache)
        svc.register("scheduler", self.scheduler)
        svc.register("notifications", self.notifications)
        svc.register("theme", self.theme)
        svc.register("security", self.security)
        svc.register("plugins", self.plugins)
        svc.register("commands", self.commands)
        svc.register("settings", self.settings)

        self._register_core_handlers()
        self._initialized = True
        self.logger.info("NEXUS Platform initialized")

    def _register_core_handlers(self) -> None:
        bus = self.event_bus

        @bus.on("plugin.*")
        async def _log_plugin_events(event):
            self.logger.info(
                "Plugin event: %s | source=%s", event.name, event.source
            )

        @bus.on("*.error")
        async def _log_errors(event):
            self.logger.error("Error event: %s | data=%s", event.name, event.data)

    async def start(self) -> None:
        self.bootstrap()
        self.logger.info("Starting NEXUS Platform...")
        await self.scheduler.start_all()
        await self.event_bus.emit("platform.started", source="platform")
        self.logger.info("NEXUS Platform started")

    async def shutdown(self) -> None:
        self.logger.info("Shutting down NEXUS Platform...")
        await self.event_bus.emit("platform.shutting_down", source="platform")
        await self.scheduler.stop_all()
        await self.container.dispose()
        self.logger.info("NEXUS Platform stopped")


platform = Platform()
