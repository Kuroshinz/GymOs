from __future__ import annotations

from datetime import datetime

from shared.intent.domain import IntentSnapshot, IntentStatus, UserIntent


class IntentVersioner:
    _snapshots: dict[str, list[IntentSnapshot]] = {}

    @classmethod
    def save_version(cls, intent: UserIntent, description: str = "") -> IntentSnapshot:
        existing = cls._snapshots.get(intent.intent_id, [])
        version = f"{len(existing) + 1}.0"
        snapshot = IntentSnapshot(
            intent=intent,
            timestamp=datetime.now().isoformat(),
            snapshot_version=version,
            score=0.0,
            change_description=description,
        )
        cls._snapshots.setdefault(intent.intent_id, []).append(snapshot)
        return snapshot

    @classmethod
    def get_history(cls, intent_id: str) -> list[IntentSnapshot]:
        return list(cls._snapshots.get(intent_id, []))

    @classmethod
    def get_version(cls, intent_id: str, version: str) -> IntentSnapshot | None:
        for s in cls._snapshots.get(intent_id, []):
            if s.snapshot_version == version:
                return s
        return None

    @classmethod
    def list_versions(cls, intent_id: str) -> list[str]:
        return [s.snapshot_version for s in cls._snapshots.get(intent_id, [])]

    @classmethod
    def rollback(cls, intent_id: str, version: str) -> UserIntent | None:
        snapshot = cls.get_version(intent_id, version)
        if snapshot is None:
            return None
        rolled = UserIntent(
            intent_id=snapshot.intent.intent_id,
            version=snapshot.intent.version,
            status=IntentStatus.ACTIVE,
            created_at=snapshot.intent.created_at,
            updated_at=datetime.now().isoformat(),
            goals=snapshot.intent.goals,
            constraints=snapshot.intent.constraints,
            timeline=snapshot.intent.timeline,
            equipment=snapshot.intent.equipment,
            lifestyle=snapshot.intent.lifestyle,
            compliance=snapshot.intent.compliance,
            risk_tolerance=snapshot.intent.risk_tolerance,
            training=snapshot.intent.training,
            nutrition=snapshot.intent.nutrition,
            recovery=snapshot.intent.recovery,
            adaptive=snapshot.intent.adaptive,
            priorities=snapshot.intent.priorities,
        )
        cls.save_version(rolled, f"Rollback to version {version}")
        return rolled

    @classmethod
    def clear(cls) -> None:
        cls._snapshots.clear()

    @classmethod
    def snapshot_count(cls) -> int:
        return sum(len(v) for v in cls._snapshots.values())
