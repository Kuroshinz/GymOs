"""Update checker — compares current version to remote manifest."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

from shared.update.manifest import fetch_manifest
from shared.version import APP_VERSION, RELEASE_CHANNEL

logger = logging.getLogger(__name__)


class UpdateAvailability(Enum):
    """Result of an update check."""
    UP_TO_DATE = auto()
    UPDATE_AVAILABLE = auto()
    NEWER_THAN_REMOTE = auto()
    CHECK_FAILED = auto()
    CHANNEL_MISMATCH = auto()


@dataclass
class UpdateCheckResult:
    """Result of checking for updates."""

    availability: UpdateAvailability
    current_version: str = APP_VERSION
    remote_version: str = ""
    release_notes_url: str = ""
    assets: list[dict[str, Any]] = field(default_factory=list)
    error: str = ""

    @property
    def has_update(self) -> bool:
        return self.availability == UpdateAvailability.UPDATE_AVAILABLE

    @property
    def message(self) -> str:
        messages = {
            UpdateAvailability.UP_TO_DATE: f"GymOS {APP_VERSION} is up to date.",
            UpdateAvailability.UPDATE_AVAILABLE: (
                f"GymOS {self.remote_version} is available "
                f"(current: {APP_VERSION})."
            ),
            UpdateAvailability.NEWER_THAN_REMOTE: (
                f"Local version {APP_VERSION} is newer than "
                f"remote {self.remote_version}."
            ),
            UpdateAvailability.CHECK_FAILED: (
                f"Update check failed: {self.error}"
            ),
            UpdateAvailability.CHANNEL_MISMATCH: (
                "Release channel mismatch."
            ),
        }
        return messages.get(self.availability, "Unknown update status.")


def parse_version(version: str) -> tuple[int, ...]:
    """Parse a semver string into a comparable tuple."""
    try:
        parts = version.replace("-", ".").split(".")
        return tuple(int(p) for p in parts if p.isdigit())
    except (ValueError, AttributeError):
        return (0, 0, 0)


def is_newer(remote_version: str, local_version: str = APP_VERSION) -> bool:
    """Compare two version strings. Returns True if remote is newer."""
    return parse_version(remote_version) > parse_version(local_version)


def is_update_available(
    remote_version: str,
    local_version: str = APP_VERSION,
) -> bool:
    """Check if a remote version is a valid update over local."""
    return is_newer(remote_version, local_version)


def get_update_manifest_url() -> str:
    """Get the URL for the update manifest based on release channel.

    Returns:
        URL string for the manifest JSON.
    """
    base = "https://gymos.app/updates"
    channel = RELEASE_CHANNEL
    if channel == "stable":
        return f"{base}/stable.json"
    return f"{base}/{channel}.json"


class UpdateChecker:
    """Periodic update checker that compares local vs remote versions."""

    def __init__(
        self,
        manifest_url: str | None = None,
        current_version: str = APP_VERSION,
    ) -> None:
        self._manifest_url = manifest_url or get_update_manifest_url()
        self._current_version = current_version
        self._last_result: UpdateCheckResult | None = None

    @property
    def last_result(self) -> UpdateCheckResult | None:
        return self._last_result

    def check(self) -> UpdateCheckResult:
        """Check for updates against the remote manifest.

        Returns:
            UpdateCheckResult with availability status.
        """
        manifest = fetch_manifest(self._manifest_url)

        if manifest is None:
            result = UpdateCheckResult(
                availability=UpdateAvailability.CHECK_FAILED,
                error=f"Could not fetch manifest from {self._manifest_url}",
            )
            self._last_result = result
            return result

        if not is_newer(manifest.app_version, self._current_version):
            result = UpdateCheckResult(
                availability=UpdateAvailability.UP_TO_DATE,
                remote_version=manifest.app_version,
            )
            self._last_result = result
            return result

        assets = [
            {
                "platform": a.platform,
                "url": a.url,
                "sha256": a.sha256,
                "size": a.size,
                "format": a.format,
            }
            for a in manifest.assets
        ]

        result = UpdateCheckResult(
            availability=UpdateAvailability.UPDATE_AVAILABLE,
            remote_version=manifest.app_version,
            release_notes_url=manifest.release_notes_url,
            assets=assets,
        )
        self._last_result = result
        return result


def check_for_updates(
    manifest_url: str | None = None,
) -> UpdateCheckResult:
    """Convenience function for a one-shot update check.

    Args:
        manifest_url: Optional custom manifest URL.

    Returns:
        UpdateCheckResult.
    """
    checker = UpdateChecker(manifest_url=manifest_url)
    return checker.check()
