from __future__ import annotations

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.command_center.models import KnowledgeUpdateItem
from ui.command_center.theme import C, Font
from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class KnowledgeUpdatesWidget(DashboardCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="Knowledge Updates", badge="LIVE", parent=parent)
        self._container = QVBoxLayout()
        self._container.setContentsMargins(0, 0, 0, 0)
        self._container.setSpacing(4)
        self.add_layout(self._container)

    def update_data(self, data: object) -> None:
        items = getattr(data, "knowledge_update_items", [])
        self.set_data(items)

    def set_data(self, items: list[KnowledgeUpdateItem]) -> None:
        self._clear()
        for item in items[:8]:
            row = QFrame()
            row.setStyleSheet(f"background-color: transparent; border-left: 2px solid {C.ACCENT}; padding-left: 8px;")
            row_layout = QVBoxLayout(row)
            row_layout.setContentsMargins(0, 4, 0, 4)
            row_layout.setSpacing(1)

            header = QHBoxLayout()
            domain_lbl = QLabel(item.domain)
            domain_lbl.setStyleSheet(f"color: {C.ACCENT}; font-size: 11px; font-weight: 600; text-transform: uppercase;")
            header.addWidget(domain_lbl)
            header.addStretch()
            version_lbl = QLabel(f"v{item.version}")
            version_lbl.setStyleSheet(Font.CAPTION)
            header.addWidget(version_lbl)
            row_layout.addLayout(header)

            statement_lbl = QLabel(item.statement)
            statement_lbl.setStyleSheet(f"color: {C.TEXT_PRIMARY}; font-size: 12px;")
            statement_lbl.setWordWrap(True)
            row_layout.addWidget(statement_lbl)

            footer = QHBoxLayout()
            conf_lbl = QLabel(f"Confidence: {item.confidence_score:.0%}")
            conf_lbl.setStyleSheet(Font.CAPTION)
            footer.addWidget(conf_lbl)
            if item.change != 0.0:
                change_text = f"{'+' if item.change > 0 else ''}{item.change:.1%}"
                change_color = C.TEXT_SUCCESS if item.change > 0 else C.TEXT_DANGER
                change_lbl = QLabel(change_text)
                change_lbl.setStyleSheet(f"color: {change_color}; font-size: 11px; font-weight: 600;")
                footer.addWidget(change_lbl)
            footer.addStretch()
            row_layout.addLayout(footer)

            self._container.addWidget(row)

    def _clear(self) -> None:
        for _i in reversed(range(self._container.count())):
            item = self._container.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()
