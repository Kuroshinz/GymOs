from __future__ import annotations

from typing import Any, Optional


class SettingsManager:
    _instance: SettingsManager | None = None

    def __new__(cls) -> SettingsManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._settings: dict[str, Any] = {}
        return cls._instance

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = self._settings
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def set(self, key: str, value: Any) -> None:
        keys = key.split(".")
        target = self._settings
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value

    def load(self, data: dict) -> None:
        self._settings.update(data)

    @property
    def all(self) -> dict:
        return self._settings
