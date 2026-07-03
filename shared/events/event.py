from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


@dataclass
class DomainEvent:
    event_name: str = ""
    event_version: str = "1.0"
    source: str = ""
    correlation_id: str = ""
    event_id: str = field(default_factory=lambda: uuid4().hex[:16])
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    _stopped: bool = field(default=False, repr=False)

    def stop_propagation(self) -> None:
        self._stopped = True

    @property
    def is_stopped(self) -> bool:
        return self._stopped

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_name": self.event_name or self.__class__.__name__,
            "event_version": self.event_version,
            "source": self.source,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp.isoformat(),
            "payload": self._payload(),
        }

    def _payload(self) -> dict[str, Any]:
        result = {}
        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                elif isinstance(value, list):
                    result[key] = [v.isoformat() if isinstance(v, datetime) else v for v in value]
                else:
                    result[key] = value
        return result

    @classmethod
    def from_dict(cls, data: dict) -> DomainEvent:
        payload = data.get("payload", {})
        payload["event_id"] = data.get("event_id", "")
        payload["event_name"] = data.get("event_name", cls.__name__)
        payload["event_version"] = data.get("event_version", "1.0")
        payload["source"] = data.get("source", "")
        payload["correlation_id"] = data.get("correlation_id", "")
        ts = data.get("timestamp")
        if ts:
            payload["timestamp"] = datetime.fromisoformat(ts)
        instance = cls(**{k: v for k, v in payload.items() if k in cls.__dataclass_fields__})
        return instance
