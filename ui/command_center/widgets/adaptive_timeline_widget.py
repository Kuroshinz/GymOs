from __future__ import annotations

from PySide6.QtWidgets import QWidget

from ui.command_center.models import AdaptiveTimelineItem
from ui.command_center.theme import C
from ui.command_center.visualization.timeline import TimelineWidget
from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class AdaptiveTimelineWidget(DashboardCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="Adaptive Timeline", parent=parent)
        self._timeline = TimelineWidget()
        self.add_content(self._timeline)

    def set_data(self, items: list[AdaptiveTimelineItem]) -> None:
        self._timeline.clear()
        for item in items:
            color = C.TEXT_SUCCESS if item.status == "approved" else C.TEXT_DANGER if item.status in ("rejected", "rolled_back") else C.TEXT_WARN
            subtitle = f"{item.adaptation_type}: {item.previous_value} → {item.new_value}"
            self._timeline.add_item(
                date=item.date,
                title=item.reason,
                subtitle=subtitle,
                color=color,
            )

    def update_data(self, data: object) -> None:
        items = getattr(data, "adaptive_timeline_items", [])
        self.set_data(items)
