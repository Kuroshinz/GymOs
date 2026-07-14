from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class Platform(StrEnum):
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"


class AppMode(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class User:
    id: str
    name: str
    email: str
    created_at: datetime


@dataclass
class Goal:
    id: str
    type: str
    target: float
    current: float
    deadline: datetime | None = None
