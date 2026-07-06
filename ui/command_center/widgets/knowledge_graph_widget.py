from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from ui.command_center.models import KnowledgeGraphData
from ui.command_center.theme import Font
from ui.command_center.visualization.relationship_graph import RelationshipGraph
from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class KnowledgeGraphWidget(DashboardCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="Knowledge Graph Overview", parent=parent)
        self._build_ui()

    def _build_ui(self) -> None:
        header = QHBoxLayout()
        self._rels_label = QLabel("")
        self._rels_label.setStyleSheet(Font.CAPTION)
        header.addWidget(self._rels_label)
        self._sync_label = QLabel("")
        self._sync_label.setStyleSheet(Font.CAPTION)
        header.addStretch()
        header.addWidget(self._sync_label)
        self.add_layout(header)

        self._graph = RelationshipGraph()
        self._graph.setMinimumHeight(160)
        self.add_content(self._graph)

    def set_data(self, data: KnowledgeGraphData) -> None:
        self._rels_label.setText(f"{data.total_relationships} relationships" if data.total_relationships else "No relationships")
        self._sync_label.setText(f"Last synced: {data.last_synced}" if data.last_synced else "")

        if data.nodes and len(data.nodes) >= 2:
            edges = [(e.get("source", 0), e.get("target", 1)) for e in data.edges[:20]]
            self._graph.set_graph(data.nodes[:10], edges)
