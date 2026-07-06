from __future__ import annotations

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui.design_system.layout import (
    EditorialGrid,
    KpiItem,
    KpiStrip,
    PanelSpan,
    ScrollContainer,
    SectionPanel,
)
from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.narrative import (
    CoachCardStack,
    Narrative,
    NarrativeEngine,
    achievement_feed,
    adaptive_summary,
    knowledge_summary,
    morning_brief,
    planning_summary,
    prediction_summary,
    recovery_summary,
    risk_alerts,
    today_focus,
)


def _dict_val(data: Any, key: str) -> dict:
    val = getattr(data, key, {})
    return val if isinstance(val, dict) else {}


class IntelligencePage(QWidget):
    generate_briefing_clicked = Signal()
    configure_ai_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._engine = NarrativeEngine()
        self._register_templates()
        self._build_ui()
        self._wire_buttons()

    def _wire_buttons(self) -> None:
        self._brief_btn.clicked.connect(self.generate_briefing_clicked.emit)
        self._config_btn.clicked.connect(self.configure_ai_clicked.emit)

    def _register_templates(self) -> None:
        self._engine.register("morning_brief", morning_brief)
        self._engine.register("today_focus", today_focus)
        self._engine.register("recovery_summary", recovery_summary)
        self._engine.register("prediction_summary", prediction_summary)
        self._engine.register("planning_summary", planning_summary)
        self._engine.register("knowledge_summary", knowledge_summary)
        self._engine.register("adaptive_summary", adaptive_summary)
        self._engine.register("risk_alerts", risk_alerts)
        self._engine.register("achievement_feed", achievement_feed)

    def _colors(self):
        return color_from_scheme(ColorScheme.DARK)

    def _build_ui(self) -> None:
        colors = self._colors()
        scroll = ScrollContainer()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        content_layout = scroll._wrapper.layout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        self._build_ai_persona_hero(content_layout)
        self._build_kpi_ribbon(content_layout)
        self._build_briefing_cards(content_layout)
        self._build_bottom_grid(content_layout)

        content_layout.addStretch()

    def _build_ai_persona_hero(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.surface};
                border-bottom: 1px solid {colors.border};
            }}
        """)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(32, 32, 32, 28)
        layout.setSpacing(12)

        top = QHBoxLayout()
        top.setSpacing(16)

        text_area = QVBoxLayout()
        text_area.setSpacing(4)

        self._hero_title = QLabel("AI Briefing Center")
        self._hero_title.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 28px; font-weight: 800; "
            f"background: transparent; border: none;"
        )
        text_area.addWidget(self._hero_title)

        self._hero_subtitle = QLabel("Coach narratives, insights, and daily briefings.")
        self._hero_subtitle.setStyleSheet(
            f"color: {colors.text_secondary}; font-size: 15px; "
            f"background: transparent; border: none;"
        )
        self._hero_subtitle.setWordWrap(True)
        text_area.addWidget(self._hero_subtitle)
        text_area.addStretch()
        top.addLayout(text_area, 1)

        actions = QVBoxLayout()
        actions.setSpacing(8)

        self._brief_btn = QPushButton("Generate Briefing")
        self._brief_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors.accent};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {colors.accent_hover};
            }}
        """)
        self._brief_btn.setCursor(Qt.PointingHandCursor)
        actions.addWidget(self._brief_btn)

        self._config_btn = QPushButton("Configure AI")
        self._config_btn.setStyleSheet(f"""
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
                border-color: {colors.accent};
                color: {colors.accent};
            }}
        """)
        self._config_btn.setCursor(Qt.PointingHandCursor)
        actions.addWidget(self._config_btn)

        top.addLayout(actions)
        layout.addLayout(top)

        self._brief_label = QLabel("AI Briefing: Ready")
        self._brief_label.setStyleSheet(
            f"color: {colors.text_primary}; font-size: 18px; font-weight: 600; "
            f"background: transparent; border: none;"
        )
        layout.addWidget(self._brief_label)

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
            KpiItem(label="Confidence", value="--", unit="%", accent=colors.accent),
            KpiItem(label="Insights", value="--", unit="", accent=colors.secondary),
            KpiItem(label="Recommendations", value="--", unit="", accent=colors.primary),
            KpiItem(label="Updates", value="--", unit="", accent=colors.info),
            KpiItem(label="Patterns", value="--", unit="", accent=colors.text_primary),
        ]
        self._kpi_strip = KpiStrip(items=kpi_items)
        layout.addWidget(self._kpi_strip)
        parent.addWidget(container)

    def _build_briefing_cards(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        container = QFrame()
        container.setStyleSheet(f"QFrame {{ background-color: {colors.background}; border: none; }}")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(32, 24, 32, 0)
        container_layout.setSpacing(12)

        self._narrative_stack = CoachCardStack()
        container_layout.addWidget(self._narrative_stack)
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

        self._update_section = SectionPanel(title="Knowledge Updates", subtitle="Recent domain changes", span=PanelSpan.HALF)
        self._update_label = QLabel("No updates.")
        self._update_label.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;"
        )
        self._update_section.add_content(self._update_label)
        grid.add_section(self._update_section)

        self._rec_detail_section = SectionPanel(title="Recommendation Details", subtitle="Actionable items", span=PanelSpan.HALF)
        self._rec_detail_label = QLabel("No recommendations.")
        self._rec_detail_label.setStyleSheet(
            f"color: {colors.text_disabled}; font-size: 13px; background: transparent; border: none;"
        )
        self._rec_detail_section.add_content(self._rec_detail_label)
        grid.add_section(self._rec_detail_section)

        parent.addWidget(container)

    def update_data(self, data: Any) -> None:
        colors = self._colors()
        planning = _dict_val(data, "planning")
        prediction = _dict_val(data, "prediction")
        recovery = _dict_val(data, "recovery")
        knowledge = _dict_val(data, "knowledge")

        recovery_overview = recovery.get("recovery_overview", {})
        training_readiness = recovery.get("training_readiness", {}) or _dict_val(data, "mission").get("training_readiness", {})
        mesocycle = planning.get("current_mesocycle", {})
        pred_summary = prediction.get("prediction_summary", {})
        insights = knowledge.get("optimization_insights", {})
        updates = knowledge.get("knowledge_updates", knowledge.get("updates", []))
        flags = recovery_overview.get("flags", [])

        narratives: list[Narrative] = []

        readiness_score = training_readiness.get("score")
        n = self._engine.render("morning_brief",
            readiness_score=readiness_score,
            recovery_score=recovery_overview.get("score"),
            fatigue_score=recovery_overview.get("fatigue_score"),
            sleep_hours=(recovery_overview.get("sleep_score", 0) or 0) / 10.0,
            today_workout=mesocycle.get("goal"),
        )
        if n:
            narratives.append(n)

        focus_str = mesocycle.get("focus", "")
        n = self._engine.render("today_focus",
            primary_goal=mesocycle.get("goal"),
            workout_type=mesocycle.get("name"),
            focus_areas=[focus_str] if focus_str else None,
            week_day=7,
        )
        if n:
            narratives.append(n)

        limiting = training_readiness.get("limiting_factor", "")
        n = self._engine.render("recovery_summary",
            recovery_score=recovery_overview.get("score"),
            sleep_hours=(recovery_overview.get("sleep_score", 0) or 0) / 10.0,
            muscle_soreness=limiting if limiting else None,
        )
        if n:
            narratives.append(n)

        preds = pred_summary.get("predictions", [])
        first_pred = preds[0] if preds else {}
        n = self._engine.render("prediction_summary",
            prediction_label=first_pred.get("label", "") if isinstance(first_pred, dict) else str(first_pred),
            confidence=pred_summary.get("accuracy"),
            metric_name=first_pred.get("metric", "") if isinstance(first_pred, dict) else "",
        )
        if n:
            narratives.append(n)

        n = self._engine.render("planning_summary",
            phase_name=mesocycle.get("phase"),
            week_number=mesocycle.get("week"),
            total_weeks=mesocycle.get("total_weeks"),
        )
        if n:
            narratives.append(n)

        first_update = updates[0] if isinstance(updates, list) and updates else {}
        n = self._engine.render("knowledge_summary",
            topic=first_update.get("domain", "") if isinstance(first_update, dict) else "",
            insight=first_update.get("statement", "") if isinstance(first_update, dict) else "",
        )
        if n:
            narratives.append(n)

        if flags:
            n = self._engine.render("risk_alerts",
                alerts=[{"title": f, "description": f, "severity": "warning"} for f in flags[:3]]
            )
            if n:
                narratives.append(n)

        insight_list = insights.get("insights", [])
        if insight_list:
            n = self._engine.render("achievement_feed",
                achievements=[
                    {"name": i if isinstance(i, str) else i.get("text", "Insight"), "points": 0}
                    for i in insight_list[:3]
                ]
            )
            if n:
                narratives.append(n)

        self._narrative_stack.clear()
        for narrative in narratives:
            self._narrative_stack.add_card(narrative)

        insight_count = len(insight_list)
        update_count = len(updates) if isinstance(updates, list) else 0
        total_patterns = insights.get("total_patterns", 0) or 0
        avg_conf = insights.get("avg_confidence", 0.0) or 0.0
        rec_count = len(planning.get("recommendations", []))

        kpi_items = [
            KpiItem(label="Confidence", value=f"{avg_conf:.0f}" if avg_conf else "--", unit="%", accent=colors.accent),
            KpiItem(label="Insights", value=str(insight_count), unit="", accent=colors.secondary),
            KpiItem(label="Recommendations", value=str(rec_count), unit="", accent=colors.primary),
            KpiItem(label="Updates", value=str(update_count), unit="", accent=colors.info),
            KpiItem(label="Patterns", value=str(total_patterns), unit="", accent=colors.text_primary),
        ]
        self._kpi_strip.set_items(kpi_items)

        self._update_label.setText(f"{update_count} updates available" if update_count else "No knowledge updates.")

        recs = planning.get("recommendations", []) or recovery.get("recommendations", [])
        self._rec_detail_section.clear()
        if recs:
            for r in recs[:3]:
                text = r if isinstance(r, str) else r.get("message", str(r))
                lbl = QLabel(f"  {text}")
                lbl.setStyleSheet(f"color: {colors.text_primary}; font-size: 13px; background: transparent; border: none;")
                lbl.setWordWrap(True)
                self._rec_detail_section.add_content(lbl)
        else:
            self._rec_detail_section.add_content(self._rec_detail_label)
