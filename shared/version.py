"""Canonical version source for GymOS.

Every version string in the application MUST import from this module.
No duplicated version strings anywhere in the codebase.
"""

from __future__ import annotations

from dataclasses import dataclass

# ── Application Version ───────────────────────────────────────────────────────

MAJOR = 0
MINOR = 5
PATCH = 0

APP_VERSION = f"{MAJOR}.{MINOR}.{PATCH}"
APP_NAME = "GymOS"
APP_DESCRIPTION = "Personal Hypertrophy Operating System"
APP_AUTHOR = "GymOS Contributors"
APP_ORGANIZATION = "GymOS Organization"
BUILD_NUMBER = 1
BUILD_DATE = "2026-07-06"
COPYRIGHT = "2024-2026 GymOS Contributors"

# ── Release Channel ───────────────────────────────────────────────────────────

RELEASE_CHANNEL = "alpha"  # "alpha", "beta", "stable"

# ── Protocol Version ──────────────────────────────────────────────────────────

PROTOCOL_MAJOR = 1
PROTOCOL_MINOR = 0
PROTOCOL_VERSION = f"{PROTOCOL_MAJOR}.{PROTOCOL_MINOR}"

# ── Database / Schema ─────────────────────────────────────────────────────────

SCHEMA_VERSION = 3          # must match Alembic head revision number
DATABASE_VERSION = 3        # bumped on breaking DB format changes

# ── Head revision tracked by Alembic ──────────────────────────────────────────

ALEMBIC_HEAD = "003"

# ── Canonical source for pyproject.toml metadata ──────────────────────────────

PYPROJECT_NAME = "gymos"
PYPROJECT_AUTHORS = ["GymOS Contributors"]
PYPROJECT_LICENSE = "MIT"
PYPROJECT_CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Environment :: Win32 (MS Windows)",
    "Environment :: X11 Applications :: Qt",
    "Intended Audience :: End Users/Desktop",
    "License :: OSI Approved :: MIT License",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Games/Entertainment",
]


# ── Version Info Dataclass ────────────────────────────────────────────────────

@dataclass(frozen=True)
class VersionInfo:
    """Complete version information for serialization / display."""
    app_version: str = APP_VERSION
    build_number: int = BUILD_NUMBER
    build_date: str = BUILD_DATE
    schema_version: int = SCHEMA_VERSION
    database_version: int = DATABASE_VERSION
    protocol_version: str = PROTOCOL_VERSION
    release_channel: str = RELEASE_CHANNEL
    alembic_head: str = ALEMBIC_HEAD

    def short(self) -> str:
        return f"{self.app_version}+build.{self.build_number}"

    def full(self) -> str:
        return (
            f"{self.app_version} ({self.release_channel}) "
            f"build {self.build_number} {self.build_date}"
        )


CURRENT = VersionInfo()
