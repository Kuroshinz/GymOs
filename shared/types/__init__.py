from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class Platform(str, Enum):
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"


class AppMode(str, Enum):
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
