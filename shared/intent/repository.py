from __future__ import annotations

from datetime import datetime

from shared.intent.domain import IntentSnapshot, IntentStatus, UserIntent


class IntentRepository:
    def __init__(self) -> None:
        self._intents: dict[str, UserIntent] = {}
        self._snapshots: dict[str, list[IntentSnapshot]] = {}

    def save(self, intent: UserIntent) -> UserIntent:
        self._intents[intent.intent_id] = intent
        return intent

    def find(self, intent_id: str) -> UserIntent | None:
        return self._intents.get(intent_id)

    def delete(self, intent_id: str) -> bool:
        return self._intents.pop(intent_id, None) is not None

    def list_active(self) -> list[UserIntent]:
        return [i for i in self._intents.values() if i.status == IntentStatus.ACTIVE]

    def list_all(self) -> list[UserIntent]:
        return list(self._intents.values())

    def count(self) -> int:
        return len(self._intents)

    def has_data(self) -> bool:
        return len(self._intents) > 0

    def save_snapshot(self, snapshot: IntentSnapshot) -> None:
        self._snapshots.setdefault(snapshot.intent.intent_id, []).append(snapshot)

    def get_snapshots(self, intent_id: str) -> list[IntentSnapshot]:
        return list(self._snapshots.get(intent_id, []))

    def clear(self) -> None:
        self._intents.clear()
        self._snapshots.clear()

    def update_status(self, intent_id: str, status: IntentStatus) -> UserIntent | None:
        intent = self.find(intent_id)
        if intent is None:
            return None
        updated = UserIntent(
            intent_id=intent.intent_id, version=intent.version, status=status,
            created_at=intent.created_at, updated_at=datetime.now().isoformat(),
            goals=intent.goals, constraints=intent.constraints,
            timeline=intent.timeline, equipment=intent.equipment,
            lifestyle=intent.lifestyle, compliance=intent.compliance,
            risk_tolerance=intent.risk_tolerance,
            training=intent.training, nutrition=intent.nutrition,
            recovery=intent.recovery, adaptive=intent.adaptive,
            priorities=intent.priorities, conflicts=intent.conflicts,
        )
        self._intents[intent_id] = updated
        return updated
