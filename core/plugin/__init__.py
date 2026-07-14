from __future__ import annotations

import importlib
import inspect
import logging
import pkgutil
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger("nexus.plugin")


@dataclass
class PluginManifest:
    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    dependencies: list[str] = field(default_factory=list)
    requires_capabilities: list[str] = field(default_factory=list)


class Plugin(ABC):
    manifest: PluginManifest

    def __init__(self) -> None:
        self._enabled = False

    @abstractmethod
    async def on_load(self) -> None: ...

    @abstractmethod
    async def on_unload(self) -> None: ...

    async def on_enable(self) -> None:
        self._enabled = True

    async def on_disable(self) -> None:
        self._enabled = False

    @property
    def is_enabled(self) -> bool:
        return self._enabled


class PluginManager:
    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}
        self._search_paths: list[Path] = []

    def add_search_path(self, path: str | Path) -> None:
        self._search_paths.append(Path(path))

    def register(self, plugin: Plugin) -> None:
        self._plugins[plugin.manifest.name] = plugin
        logger.info("Plugin registered: %s v%s", plugin.manifest.name, plugin.manifest.version)

    def get(self, name: str) -> Plugin | None:
        return self._plugins.get(name)

    def discover(self, package_path: str | Path | None = None) -> list[type[Plugin]]:
        discovered: list[type[Plugin]] = []
        paths = self._search_paths[:]
        if package_path:
            paths.append(Path(package_path))

        for search_path in paths:
            if not search_path.exists():
                continue
            for module_info in pkgutil.iter_modules([str(search_path)]):
                try:
                    module = importlib.import_module(module_info.name)
                    for _, obj in inspect.getmembers(module, inspect.isclass):
                        if (
                            issubclass(obj, Plugin)
                            and obj is not Plugin
                            and hasattr(obj, "manifest")
                        ):
                            discovered.append(obj)
                except Exception:
                    logger.exception("Failed to discover plugin in %s", module_info.name)
        return discovered

    async def load_all(self) -> None:
        for name, plugin in list(self._plugins.items()):
            try:
                await plugin.on_load()
                logger.info("Plugin loaded: %s", name)
            except Exception:
                logger.exception("Failed to load plugin: %s", name)

    async def unload_all(self) -> None:
        for name, plugin in list(self._plugins.items()):
            try:
                await plugin.on_unload()
                logger.info("Plugin unloaded: %s", name)
            except Exception:
                logger.exception("Failed to unload plugin: %s", name)

    @property
    def all(self) -> dict[str, Plugin]:
        return dict(self._plugins)
