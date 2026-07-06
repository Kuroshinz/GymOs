"""Download verification — SHA256 checksum validation."""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def sha256_file(path: str | Path) -> str:
    """Compute SHA256 hash of a file.

    Args:
        path: Path to the file.

    Returns:
        Hex-encoded SHA256 string.
    """
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_checksum(
    file_path: str | Path,
    expected_sha256: str,
) -> bool:
    """Verify a file's SHA256 checksum.

    Args:
        file_path: Path to the downloaded file.
        expected_sha256: Expected hex-encoded SHA256.

    Returns:
        True if checksum matches, False otherwise.
    """
    actual = sha256_file(file_path)
    match = actual.lower() == expected_sha256.lower()
    if not match:
        logger.error(
            "Checksum mismatch for %s:\n  expected: %s\n  actual:   %s",
            file_path, expected_sha256, actual,
        )
    return match


def verify_checksum_file(
    file_path: str | Path,
    checksums_file: str | Path,
    expected_basename: str | None = None,
) -> bool:
    """Verify a file against a SHA256SUMS file.

    Args:
        file_path: Path to the file to verify.
        checksums_file: Path to SHA256SUMS.txt.
        expected_basename: Expected filename in checksums file
                           (defaults to file_path's basename).

    Returns:
        True if checksum matches, False otherwise.
    """
    file_path = Path(file_path)
    checksums_file = Path(checksums_file)
    basename = expected_basename or file_path.name

    if not checksums_file.exists():
        logger.error("Checksums file not found: %s", checksums_file)
        return False

    for line in checksums_file.read_text(encoding="utf-8").strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 2)
        if len(parts) >= 2 and parts[1] == basename:
            return verify_checksum(file_path, parts[0])

    logger.error(
        "File %s not found in checksums file %s",
        basename, checksums_file,
    )
    return False
