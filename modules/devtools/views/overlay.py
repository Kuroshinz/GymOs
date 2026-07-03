"""Developer overlay — optional HUD showing real-time system state."""

from __future__ import annotations

from typing import Any

from modules.devtools.services.devtool_service import DevToolsService


class DevToolsOverlay:
    """Optional developer overlay.

    Displays real-time system information:
    - Event count
    - Events/sec
    - Subscriber count
    - Log count / error count
    - Health status
    - Replay status
    - Uptime

    Can be toggled on/off. Never affects production behavior.
    """

    def __init__(self, service: DevToolsService | None = None) -> None:
        self._service = service or DevToolsService()
        self._visible = False

    def show(self) -> None:
        self._visible = True

    def hide(self) -> None:
        self._visible = False

    def toggle(self) -> bool:
        self._visible = not self._visible
        return self._visible

    @property
    def visible(self) -> bool:
        return self._visible

    def render(self) -> dict[str, Any]:
        if not self._visible:
            return {"visible": False}
        state = self._service.get_state()
        return {
            "visible": True,
            "state": state.to_dict(),
            "lines": self._format_lines(state),
        }

    def _format_lines(self, state: Any) -> list[str]:
        return [
            f"DevTools {'ON' if self._service.console.enabled else 'OFF'}",
            f"Events: {state.event_count} ({state.events_per_sec}/s)",
            f"Subscribers: {state.subscriber_count}",
            f"Logs: {state.log_count} (E:{state.error_count})",
            f"Health: {state.health_status}",
            f"Uptime: {state.uptime_seconds:.0f}s",
        ]

    def get_lines(self) -> list[str]:
        if not self._visible:
            return []
        return self._format_lines(self._service.get_state())
