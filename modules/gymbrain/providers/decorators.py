"""Decorators for GymBrain providers — standardized error handling.

Eliminates repetitive try/except boilerplate across provider methods.
Usage::

    class MyProvider:
        @safe(default=None)
        def get_something(self, key: str) -> dict | None:
            return self._repo.get(key)

        @safe(default=[])
        def get_all(self) -> list:
            return self._repo.list()
"""

from __future__ import annotations

import functools
import logging
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

logger = logging.getLogger(__name__)

P = ParamSpec("P")
R = TypeVar("R")


def safe(
    default: R = None,  # type: ignore[assignment]
    message: str | None = None,
) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """Wrap a method with try/except, logging, and a fallback return value.

    The decorated method's normal return passes through unchanged.
    On any ``Exception`` the exception is logged via ``logger.warning(..., exc_info=True)``
    and *default* is returned instead.

    Args:
        default: Fallback return value when an exception occurs.
                 If callable, it is invoked with no arguments and the result is returned.
        message: Custom log message template. Receives the method name as ``%s``.
                 Defaults to ``"<method_name> failed"``.
    """
    def decorator(func: Callable[..., R]) -> Callable[..., R]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> R:
            try:
                return func(*args, **kwargs)
            except Exception:
                msg = message or "%s failed"
                logger.warning(msg, func.__name__, exc_info=True)
                result = default() if callable(default) else default
                return result  # type: ignore[return-value]
        return wrapper
    return decorator


__all__ = ["safe"]
