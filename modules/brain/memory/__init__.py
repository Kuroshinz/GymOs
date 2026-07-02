from typing import Any, Optional


class Memory:
    _instance: Optional["Memory"] = None

    def __new__(cls) -> "Memory":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._store: dict[str, Any] = {}
            cls._instance._conversation_history: list[dict] = []
        return cls._instance

    def remember(self, key: str, value: Any) -> None:
        self._store[key] = value

    def recall(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def add_message(self, role: str, content: str) -> None:
        self._conversation_history.append({"role": role, "content": content})

    def get_context(self, limit: int = 10) -> list[dict]:
        return self._conversation_history[-limit:]

    def clear(self) -> None:
        self._store.clear()
        self._conversation_history.clear()
