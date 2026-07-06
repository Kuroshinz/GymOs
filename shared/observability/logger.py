"""Structured logging — unified logging layer with severity, context, correlation_id."""

from __future__ import annotations

import logging
import threading
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


@dataclass
class LogEntry:
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    level: str = "INFO"
    module: str = ""
    message: str = ""
    correlation_id: str = ""
    event_id: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    duration_ms: float | None = None
    thread: str = field(default_factory=lambda: threading.current_thread().name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "level": self.level,
            "module": self.module,
            "message": self.message,
            "correlation_id": self.correlation_id,
            "event_id": self.event_id,
            "context": self.context,
            "duration_ms": self.duration_ms,
            "thread": self.thread,
        }


class StructuredLogger:
    """Unified structured logger.

    Writes to both Python's logging and an in-memory buffer for inspection.
    Every log entry carries module, severity, correlation_id, and context.
    """

    def __init__(self, name: str = "nexus", buffer_size: int = 1000) -> None:
        self._name = name
        self._buffer: list[LogEntry] = []
        self._buffer_size = buffer_size
        self._py_logger = logging.getLogger(name)

    @property
    def name(self) -> str:
        return self._name

    def _log(
        self,
        level: LogLevel,
        message: str,
        module: str = "",
        correlation_id: str = "",
        event_id: str = "",
        context: dict[str, Any] | None = None,
        duration_ms: float | None = None,
    ) -> LogEntry:
        entry = LogEntry(
            level=level.value,
            module=module,
            message=message,
            correlation_id=correlation_id,
            event_id=event_id,
            context=context or {},
            duration_ms=duration_ms,
        )
        self._buffer.append(entry)
        if len(self._buffer) > self._buffer_size:
            self._buffer.pop(0)

        log_fn = {
            LogLevel.DEBUG: self._py_logger.debug,
            LogLevel.INFO: self._py_logger.info,
            LogLevel.WARNING: self._py_logger.warning,
            LogLevel.ERROR: self._py_logger.error,
        }[level]
        log_fn(
            "[%s] %s%s%s",
            module or self._name,
            message,
            f" (correlation_id={correlation_id})" if correlation_id else "",
            f" ({duration_ms:.1f}ms)" if duration_ms is not None else "",
            extra={
                "nexus_correlation_id": correlation_id,
                "nexus_event_id": event_id,
                "nexus_module": module or self._name,
            },
        )
        return entry

    def debug(
        self,
        message: str,
        module: str = "",
        correlation_id: str = "",
        event_id: str = "",
        context: dict[str, Any] | None = None,
    ) -> LogEntry:
        return self._log(LogLevel.DEBUG, message, module, correlation_id, event_id, context)

    def info(
        self,
        message: str,
        module: str = "",
        correlation_id: str = "",
        event_id: str = "",
        context: dict[str, Any] | None = None,
        duration_ms: float | None = None,
    ) -> LogEntry:
        return self._log(LogLevel.INFO, message, module, correlation_id, event_id, context, duration_ms)

    def warning(
        self,
        message: str,
        module: str = "",
        correlation_id: str = "",
        event_id: str = "",
        context: dict[str, Any] | None = None,
    ) -> LogEntry:
        return self._log(LogLevel.WARNING, message, module, correlation_id, event_id, context)

    def error(
        self,
        message: str,
        module: str = "",
        correlation_id: str = "",
        event_id: str = "",
        context: dict[str, Any] | None = None,
        duration_ms: float | None = None,
    ) -> LogEntry:
        return self._log(LogLevel.ERROR, message, module, correlation_id, event_id, context, duration_ms)

    def search(self, query: str) -> list[LogEntry]:
        """Search logs by message content."""
        q = query.lower()
        return [e for e in self._buffer if q in e.message.lower() or q in e.module.lower()]

    def filter_by_level(self, level: LogLevel) -> list[LogEntry]:
        return [e for e in self._buffer if e.level == level.value]

    def filter_by_module(self, module: str) -> list[LogEntry]:
        return [e for e in self._buffer if e.module == module]

    def filter_by_correlation_id(self, correlation_id: str) -> list[LogEntry]:
        return [e for e in self._buffer if e.correlation_id == correlation_id]

    def get_recent(self, n: int = 50) -> list[LogEntry]:
        return self._buffer[-n:]

    def export(self) -> list[dict[str, Any]]:
        return [e.to_dict() for e in self._buffer]

    def clear(self) -> None:
        self._buffer.clear()

    @property
    def count(self) -> int:
        return len(self._buffer)

    def error_count(self) -> int:
        return sum(1 for e in self._buffer if e.level == "ERROR")

    def warning_count(self) -> int:
        return sum(1 for e in self._buffer if e.level == "WARNING")


_logger_instance: StructuredLogger | None = None


def get_logger(name: str = "nexus") -> StructuredLogger:
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = StructuredLogger(name)
    return _logger_instance
