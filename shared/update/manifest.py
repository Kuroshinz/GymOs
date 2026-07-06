"""Release manifest — version metadata for auto-update."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from shared.version import (
    APP_VERSION,
    BUILD_NUMBER,
    RELEASE_CHANNEL,
    SCHEMA_VERSION,
)

logger = logging.getLogger(__name__)

MANIFEST_VERSION = 1
MANIFEST_FILENAME = "update_manifest.json"


@dataclass
class BuildAsset:
    """A downloadable build artifact."""

    platform: str        # "windows", "linux", "macos"
    url: str             # Download URL
    sha256: str          # SHA256 checksum
    size: int            # File size in bytes
    format: str = ""     # "exe", "msi", "zip", "AppImage", "deb", "dmg"


@dataclass
class ReleaseManifest:
    """Complete release manifest for update checking."""

    app_version: str
    build_number: int
    release_channel: str
    schema_version: int
    release_date: str
    min_app_version: str
    release_notes_url: str
    assets: list[BuildAsset] = field(default_factory=list)
    manifest_version: int = MANIFEST_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "manifest_version": self.manifest_version,
            "app_version": self.app_version,
            "build_number": self.build_number,
            "release_channel": self.release_channel,
            "schema_version": self.schema_version,
            "release_date": self.release_date,
            "min_app_version": self.min_app_version,
            "release_notes_url": self.release_notes_url,
            "assets": [
                {
                    "platform": a.platform,
                    "url": a.url,
                    "sha256": a.sha256,
                    "size": a.size,
                    "format": a.format,
                }
                for a in self.assets
            ],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ReleaseManifest:
        assets = [
            BuildAsset(
                platform=a["platform"],
                url=a["url"],
                sha256=a["sha256"],
                size=a["size"],
                format=a.get("format", ""),
            )
            for a in data.get("assets", [])
        ]
        return cls(
            app_version=data["app_version"],
            build_number=data["build_number"],
            release_channel=data.get("release_channel", "stable"),
            schema_version=data.get("schema_version", 1),
            release_date=data.get("release_date", ""),
            min_app_version=data.get("min_app_version", "0.0.0"),
            release_notes_url=data.get("release_notes_url", ""),
            assets=assets,
            manifest_version=data.get("manifest_version", 1),
        )


def generate_manifest(assets: list[BuildAsset] | None = None) -> ReleaseManifest:
    """Generate the current release manifest.

    Used at build time to create the update_manifest.json for distribution.

    Args:
        assets: List of build assets to include.

    Returns:
        ReleaseManifest for the current version.
    """
    return ReleaseManifest(
        app_version=APP_VERSION,
        build_number=BUILD_NUMBER,
        release_channel=RELEASE_CHANNEL,
        schema_version=SCHEMA_VERSION,
        release_date=datetime.now().strftime("%Y-%m-%d"),
        min_app_version="0.1.0",
        release_notes_url=f"https://github.com/gymos/gymos/releases/v{APP_VERSION}",
        assets=assets or [],
    )


def write_manifest(manifest: ReleaseManifest, path: str | Path) -> None:
    """Write a release manifest to disk.

    Args:
        manifest: The manifest to write.
        path: Output file path.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(manifest.to_dict(), indent=2),
        encoding="utf-8",
    )
    logger.info("Release manifest written to %s", path)


def parse_manifest(content: str) -> ReleaseManifest | None:
    """Parse a JSON manifest string into a ReleaseManifest.

    Args:
        content: JSON string.

    Returns:
        ReleaseManifest or None on failure.
    """
    try:
        data = json.loads(content)
        return ReleaseManifest.from_dict(data)
    except (json.JSONDecodeError, KeyError) as e:
        logger.error("Failed to parse manifest: %s", e)
        return None


def fetch_manifest(url: str) -> ReleaseManifest | None:
    """Fetch and parse a remote release manifest.

    Args:
        url: URL to the manifest JSON.

    Returns:
        ReleaseManifest or None on failure.
    """
    try:
        import urllib.request

        with urllib.request.urlopen(url, timeout=10) as response:
            content = response.read().decode("utf-8")
            return parse_manifest(content)
    except Exception as e:
        logger.error("Failed to fetch manifest from %s: %s", url, e)
        return None
