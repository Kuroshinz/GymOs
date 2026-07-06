from __future__ import annotations

from PySide6.QtWidgets import QWidget

from ui.command_center.models import DecisionTimelineItem
from ui.command_center.theme import C
from ui.command_center.visualization.timeline import TimelineWidget
from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class DecisionTimelineWidget(DashboardCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="Decision Timeline", parent=parent)
        self._timeline = TimelineWidget()
        self.add_content(self._timeline)

    def set_data(self, items: list[DecisionTimelineItem]) -> None:
        self._timeline.clear()
        for item in items:
            color = C.TEXT_SUCCESS if item.outcome == "approved" else C.TEXT_DANGER if item.outcome == "rejected" else C.TEXT_WARN
            subtitle = f"Confidence: {item.confidence:.0%} · Impact: {item.impact}"
            self._timeline.add_item(
                date=item.date,
                title=item.decision_type,
                subtitle=subtitle,
                color=color,
            )

    def update_data(self, data: object) -> None:
        items = getattr(data, "decision_timeline_items", [])
        self.set_data(items)
