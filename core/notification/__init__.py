from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class NotificationPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Notification:
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    source: str = "system"
    data: dict = field(default_factory=dict)


class NotificationService:
    _instance: NotificationService | None = None

    def __new__(cls) -> NotificationService:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._handlers: list = []
        return cls._instance

    def register_handler(self, handler) -> None:
        self._handlers.append(handler)

    def send(self, notification: Notification) -> None:
        for handler in self._handlers:
            handler(notification)
