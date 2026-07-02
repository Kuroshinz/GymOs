from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class Command:
    name: str
    handler: Callable
    description: str = ""
    args: list = field(default_factory=list)


class CommandBus:
    _instance: Optional["CommandBus"] = None

    def __new__(cls) -> "CommandBus":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._commands: dict[str, Command] = {}
        return cls._instance

    def register(self, command: Command) -> None:
        self._commands[command.name] = command

    async def execute(self, name: str, *args: Any, **kwargs: Any) -> Any:
        command = self._commands.get(name)
        if not command:
            raise KeyError(f"Command '{name}' not found")
        return command.handler(*args, **kwargs)

    def unregister(self, name: str) -> None:
        self._commands.pop(name, None)
