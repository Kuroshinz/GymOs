"""Version Manager — Semantic versioning and snapshot management for knowledge evolution."""

from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime

from shared.knowledge_evolution.domain import (
    KnowledgeConflict,
    KnowledgeRecord,
    KnowledgeSnapshot,
    KnowledgeVersion,
)


def _generate_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


_VERSION_PATTERN = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")


def _parse_version(version: str) -> tuple[int, int, int]:
    match = _VERSION_PATTERN.match(version)
    if not match:
        raise ValueError(f"Invalid version format: {version!r}")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def _increment_minor(major: int, minor: int, _patch: int) -> str:
    return f"v{major}.{minor + 1}.0"


class VersionManager:
    """Manages semantic versioning, snapshots, and rollback for knowledge records."""

    def create_version(
        self,
        knowledge_record: KnowledgeRecord,
        parent_version: str = "",
    ) -> KnowledgeVersion:
        if not parent_version:
            version = "v1.0.0"
        else:
            parts = _parse_version(parent_version)
            version = _increment_minor(*parts)

        return KnowledgeVersion(
            version_id=_generate_id("ver"),
            knowledge_id=knowledge_record.knowledge_id,
            version=version,
            parent_version=parent_version,
            record=knowledge_record,
            created_at=datetime.now(UTC).isoformat(),
            description="",
        )

    def create_snapshot(
        self,
        records: list[KnowledgeRecord],
        conflicts: list[KnowledgeConflict],
        description: str = "",
    ) -> KnowledgeSnapshot:
        now = datetime.now(UTC)
        version = f"snap_{now.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

        return KnowledgeSnapshot(
            snapshot_id=_generate_id("snap"),
            version=version,
            records=records,
            conflicts=conflicts,
            created_at=now.isoformat(),
            description=description,
        )

    def get_version_history(
        self,
        all_versions: list[KnowledgeVersion],
        knowledge_id: str,
    ) -> list[KnowledgeVersion]:
        return sorted(
            (v for v in all_versions if v.knowledge_id == knowledge_id),
            key=lambda v: _parse_version(v.version),
        )

    def rollback_to_version(
        self,
        all_versions: list[KnowledgeVersion],
        knowledge_id: str,
        target_version: str,
    ) -> KnowledgeVersion | None:
        _parse_version(target_version)
        for v in all_versions:
            if v.knowledge_id == knowledge_id and v.version == target_version:
                return v
        return None
