"""Auto-update module for GymOS.

Provides version checking, update manifest parsing,
download verification, and release channel selection.
"""

from shared.update.checker import (
    UpdateChecker,
    UpdateCheckResult,
    check_for_updates,
    get_update_manifest_url,
)
from shared.update.manifest import (
    BuildAsset,
    ReleaseManifest,
    fetch_manifest,
    parse_manifest,
)
from shared.update.verifier import (
    sha256_file,
    verify_checksum,
    verify_checksum_file,
)

__all__ = [
    "UpdateCheckResult",
    "UpdateChecker",
    "check_for_updates",
    "get_update_manifest_url",
    "BuildAsset",
    "ReleaseManifest",
    "fetch_manifest",
    "parse_manifest",
    "sha256_file",
    "verify_checksum",
    "verify_checksum_file",
]
