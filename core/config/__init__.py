from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

class Config:
    _instance: Optional["Config"] = None

    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._data: Dict[str, Any] = {}
            cls._instance._env_prefix = "NEXUS_"
        return cls._instance

    def load(self, path: str | Path) -> None:
        path = Path(path)
        if path.suffix == ".json":
            with open(path) as f:
                self._data.update(json.load(f))
        elif path.suffix in (".yml", ".yaml"):
            try:
                import yaml
                with open(path) as f:
                    self._data.update(yaml.safe_load(f))
            except ImportError:
                raise ImportError("PyYAML is required to load YAML config files")
        else:
            raise ValueError(f"Unsupported config format: {path.suffix}")

    def load_env(self, prefix: str | None = None) -> None:
        prefix = prefix or self._env_prefix
        for key, value in os.environ.items():
            if key.startswith(prefix):
                config_key = key[len(prefix):].lower()
                self._data[config_key] = value

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        value = self._data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def set(self, key: str, value: Any) -> None:
        keys = key.split(".")
        target = self._data
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value

    @property
    def all(self) -> Dict[str, Any]:
        return self._data
