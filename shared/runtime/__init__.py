from __future__ import annotations

from shared.runtime.runtime import Runtime


def create_runtime(
    event_bus=None,
    services=None,
    scheduler=None,
    config=None,
) -> Runtime:
    return Runtime(
        event_bus=event_bus,
        services=services,
        scheduler=scheduler,
        config=config,
    )


__all__ = ["create_runtime", "Runtime"]
