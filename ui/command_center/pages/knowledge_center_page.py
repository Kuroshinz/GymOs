from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.design_system.components import (
    InsightCard,
)
from ui.design_system.layout import (
    EditorialGrid,
    KpiItem,
    KpiStrip,
    PanelSpan,
    ScrollContainer,
    SectionPanel,
)
from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.visualization import ConfidenceGauge


class KnowledgeCenterPage(QWidget):
    explore_graph_clicked = Signal()
    search_knowledge_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()
        self._wire_buttons()

    def _wire_buttons(self) -> None:
        self._explore_btn.clicked.connect(self.explore_graph_clicked.emit)
        self._search_btn.clicked.connect(self.search_knowledge_clicked.emit)

    def _colors(self):
        return color_from_scheme(ColorScheme.DARK)

    def _build_ui(self) -> None:
        scroll = ScrollContainer()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        content_layout = scroll._wrapper.layout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self._build_graph_header(content_layout)
        self._build_kpi_ribbon(content_layout)
        self._build_updates_timeline(content_layout)
        self._build_bottom_grid(content_layout)

        content_layout.addStretch()

    def _build_graph_header(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.surface};
                border-bottom: 1px solid {colors.border};
            }}
        """)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(32, 32, 32, 28)
        layout.setSpacing(24)

        text_area = QVBoxLayout()
        text_area.setSpacing(4)

        self._hero_title = QLabel("Knowledge Explorer")
        self._hero_title.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 28px; font-weight: 800; "
            f"background: transparent; border: none;"
        )
        text_area.addWidget(self._hero_title)

        self._hero_subtitle = QLabel("Domain knowledge evolution, confidence tracking, and pattern discovery.")
        self._hero_subtitle.setStyleSheet(
            f"color: {colors.text_secondary}; font-size: 15px; "
            f"background: transparent; border: none;"
        )
        self._hero_subtitle.setWordWrap(True)
        text_area.addWidget(self._hero_subtitle)
        text_area.addStretch()
        layout.addLayout(text_area, 1)

        graph_stats = QHBoxLayout()
        graph_stats.setSpacing(24)

        self._nodes_label = QLabel("Nodes: --")
        self._nodes_label.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 18px; font-weight: 700; "
            f"background: transparent; border: none;"
        )
        graph_stats.addWidget(self._nodes_label)

        self._edges_label = QLabel("Edges: --")
        self._edges_label.setStyleSheet(
            f"color: {colors.text_secondary}; font-size: 18px; font-weight: 600; "
            f"background: transparent; border: none;"
        )
        graph_stats.addWidget(self._edges_label)

        layout.addLayout(graph_stats)

        actions = QVBoxLayout()
        actions.setSpacing(8)

        self._explore_btn = QPushButton("Explore Graph")
        self._explore_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.secondary};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {colors.secondary_hover};
            }}
        """)
        self._explore_btn.setCursor(Qt.PointingHandCursor)
        actions.addWidget(self._explore_btn)

        self._search_btn = QPushButton("Search Knowledge")
        self._search_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {colors.text_secondary};
                border: 1px solid {colors.border};
                border-radius: 8px;
                padding: 8px 24px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                border-color: {colors.secondary};
                color: {colors.secondary};
            }}
        """)
        self._search_btn.setCursor(Qt.PointingHandCursor)
        actions.addWidget(self._search_btn)

        layout.addLayout(actions)
        parent.addWidget(container)

    def _build_kpi_ribbon(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.background};
                border-bottom: 1px solid {colors.border};
            }}
        """)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 0, 32, 0)

        kpi_items = [
            KpiItem(label="Insights", value="--", unit="", accent=colors.secondary),
            KpiItem(label="Reliable", value="--", unit="%", accent=colors.success),
            KpiItem(label="Updates", value="--", unit="", accent=colors.info),
            KpiItem(label="Confidence", value="--", unit="%", accent=colors.accent),
            KpiItem(label="Patterns", value="--", unit="", accent=colors.text_primary),
            KpiItem(label="New", value="--", unit="", accent=colors.success),
            KpiItem(label="Changed", value="--", unit="", accent=colors.warning),
        ]
        self._kpi_strip = KpiStrip(items=kpi_items)
        layout.addWidget(self._kpi_strip)
        parent.addWidget(container)

    def _build_updates_timeline(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"QFrame {{ background-color: {colors.background}; border: none; }}")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(32, 24, 32, 0)
        container_layout.setSpacing(12)

        self._timeline_section = SectionPanel(title="Knowledge Updates", subtitle="Recent domain changes and discoveries")

        self._updates_widget = QWidget()
        self._updates_layout = QVBoxLayout(self._updates_widget)
        self._updates_layout.setContentsMargins(0, 0, 0, 0)
        self._updates_layout.setSpacing(6)
        no_data = QLabel("No knowledge updates.")
        no_data.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;"
        )
        self._updates_layout.addWidget(no_data)
        self._timeline_section.add_content(self._updates_widget)
        container_layout.addWidget(self._timeline_section)
        parent.addWidget(container)

    def _build_bottom_grid(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"QFrame {{ background-color: {colors.background}; border: none; }}")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(32, 16, 32, 32)
        container_layout.setSpacing(16)

        grid = EditorialGrid()
        grid.set_spacing(16)
        container_layout.addWidget(grid)

        self._insight_section = SectionPanel(title="Top Insights", subtitle="Highest confidence patterns", span=PanelSpan.HALF)
        self._insight_label = QLabel("No insights available.")
        self._insight_label.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;"
        )
        self._insight_section.add_content(self._insight_label)
        grid.add_section(self._insight_section)

        self._confidence_section = SectionPanel(title="Confidence Trend", subtitle="Pattern confidence over time", span=PanelSpan.HALF)
        self._confidence_gauge = ConfidenceGauge(width=200, height=30)
        self._confidence_gauge.set_confidence(0.0, "Avg Pattern Confidence")
        self._confidence_section.add_content(self._confidence_gauge)
        grid.add_section(self._confidence_section)

        parent.addWidget(container)

    def update_data(self, data: Any) -> None:
        colors = self._colors()
        knowledge = _dict_val(data, "knowledge")

        kg = knowledge.get("knowledge_graph", {})
        nodes = kg.get("nodes", []) if kg else []
        relationships = kg.get("total_relationships", 0) or 0

        self._nodes_label.setText(f"Nodes: {len(nodes)}")
        self._edges_label.setText(f"Relationships: {relationships}")

        insights_data = knowledge.get("optimization_insights", {})
        insight_list = insights_data.get("insights", [])
        total_patterns = insights_data.get("total_patterns", 0) or 0
        reliable = insights_data.get("reliable_patterns", 0) or 0
        avg_conf = insights_data.get("avg_confidence", 0.0) or 0.0

        updates = knowledge.get("knowledge_updates", []) or knowledge.get("updates", [])
        new_count = sum(1 for u in updates if isinstance(u, dict) and u.get("change", 0) > 0) if updates else 0
        changed_count = len(updates) - new_count if updates else 0

        kpi_items = [
            KpiItem(label="Insights", value=str(len(insight_list)), unit="", accent=colors.secondary),
            KpiItem(label="Reliable", value=f"{reliable}", unit="%", accent=colors.success),
            KpiItem(label="Updates", value=str(len(updates)), unit="", accent=colors.info),
            KpiItem(label="Confidence", value=f"{avg_conf:.0f}", unit="%", accent=colors.accent),
            KpiItem(label="Patterns", value=str(total_patterns), unit="", accent=colors.text_primary),
            KpiItem(label="New", value=str(new_count), unit="", accent=colors.success),
            KpiItem(label="Changed", value=str(changed_count), unit="", accent=colors.warning),
        ]
        self._kpi_strip.set_items(kpi_items)

        self._updates_layout = self._updates_widget.layout()
        self._clear_layout(self._updates_layout)
        if updates:
            for upd in updates[:6]:
                text = upd if isinstance(upd, str) else upd.get("statement", str(upd))
                domain = upd.get("domain", "") if isinstance(upd, dict) else ""
                icon = ""
                lbl = QLabel(f"  {icon}  {text}" + (f"  [{domain}]" if domain else ""))
                lbl.setStyleSheet(f"color: {colors.text_primary}; font-size: 13px; background: transparent; border: none;")
                lbl.setWordWrap(True)
                self._updates_layout.addWidget(lbl)
        else:
            no_data = QLabel("No knowledge updates.")
            no_data.setStyleSheet(f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;")
            self._updates_layout.addWidget(no_data)

        self._insight_section.clear()
        if insight_list:
            for ins in insight_list[:4]:
                text = ins if isinstance(ins, str) else ins.get("text", str(ins))
                card = InsightCard(icon="", title=text, description="", badge_text="Pattern")
                self._insight_section.add_content(card)
        else:
            lbl = QLabel("No insights available.")
            lbl.setStyleSheet(f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;")
            self._insight_section.add_content(lbl)

        self._confidence_gauge.set_confidence(avg_conf / 100 if avg_conf > 1 else avg_conf, "Avg Pattern Confidence")

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()


def _dict_val(data: Any, key: str) -> dict:
    val = getattr(data, key, {})
    return val if isinstance(val, dict) else {}
