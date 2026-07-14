from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from modules.prediction.domain import (
    PredictionResult,
)
from modules.prediction.presentation import (
    PredictionFormatter,
    PredictionViewModel,
)
from ui.design_system.components.insight_card import InsightCard
from ui.design_system.components.section_header import SectionHeader
from ui.design_system.components.status_badge import StatusBadge, StatusLevel
from ui.design_system.layout import PanelSpan, SectionPanel
from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.design_system.tokens.radius import RadiusTokens, px_from_token
from ui.design_system.tokens.spacing import SpacingTokens
from ui.design_system.tokens.typography import TypographyTokens, font_style
from ui.design_system.visualization import ConfidenceGauge, PredictionTimeline
from ui.design_system.visualization.risk_meter import RiskMeter

S = SpacingTokens()
R = RadiusTokens()
T = TypographyTokens()

_px4 = px_from_token(S.s1)
_px6 = px_from_token(S.s1_5)
_px8 = px_from_token(S.s2)
_px12 = px_from_token(S.s3)
_px16 = px_from_token(S.s4)
_px24 = px_from_token(S.s6)
_px32 = px_from_token(S.s8)


@dataclass
class PredictionDashboardData:
    view_model: PredictionViewModel = field(default_factory=PredictionViewModel)
    has_data: bool = False
    result: PredictionResult | None = None


class PredictionDashboard(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._data: PredictionDashboardData | None = None
        self._build_ui()

    def _colors(self):
        return color_from_scheme(ColorScheme.DARK)

    def _build_ui(self) -> None:
        from ui.design_system.layout.scroll_container import ScrollContainer
        scroll = ScrollContainer()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        main = QVBoxLayout()
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(0)
        scroll.content_layout.insertLayout(0, main)

        self._build_hero(main)

        self._build_section_header(main, "Prediction Overview", "Forecasts across key training metrics")
        self._card_grid = QGridLayout()
        self._card_grid.setContentsMargins(0, 0, 0, 0)
        self._card_grid.setSpacing(_px12)
        main.addLayout(self._card_grid)
        self._pred_cards = []

        self._build_section_header(main, "Forecast Timeline", "Projected trend over time")
        self._timeline_panel = SectionPanel(title="Timeline", subtitle="Prediction across forecast window", span=PanelSpan.FULL)
        self._timeline_chart = PredictionTimeline()
        self._timeline_panel.add_content(self._timeline_chart)
        self._timeline_empty = QLabel("No timeline data available")
        self._timeline_empty.setStyleSheet(f"color: {self._colors().text_disabled}; {font_style('body_small')}")
        self._timeline_empty.setAlignment(Qt.AlignCenter)
        self._timeline_panel.add_content(self._timeline_empty)
        self._timeline_chart.hide()
        main.addWidget(self._timeline_panel)

        self._build_section_header(main, "Confidence & Risk", "Prediction reliability and uncertainty")
        self._confidence_risk_row = QHBoxLayout()
        self._confidence_risk_row.setSpacing(_px16)

        self._confidence_panel = SectionPanel(title="Confidence", subtitle="Overall prediction confidence", span=PanelSpan.HALF)
        self._confidence_gauge = ConfidenceGauge(width=280, height=40)
        self._confidence_panel.add_content(self._confidence_gauge)
        self._confidence_detail = QLabel("")
        self._confidence_detail.setStyleSheet(f"color: {self._colors().text_disabled}; {font_style('caption')}")
        self._confidence_detail.setAlignment(Qt.AlignCenter)
        self._confidence_panel.add_content(self._confidence_detail)
        self._confidence_row_widget = QWidget()
        self._confidence_row_widget.setLayout(self._confidence_risk_row)

        self._risk_panel = SectionPanel(title="Risk", subtitle="Uncertainty and volatility metrics", span=PanelSpan.HALF)
        self._risk_meter = RiskMeter(width=200, height=28)
        self._risk_panel.add_content(self._risk_meter)
        self._risk_detail = QLabel("")
        self._risk_detail.setStyleSheet(f"color: {self._colors().text_disabled}; {font_style('caption')}")
        self._risk_detail.setAlignment(Qt.AlignCenter)
        self._risk_panel.add_content(self._risk_detail)

        self._confidence_risk_row.addWidget(self._confidence_panel)
        self._confidence_risk_row.addWidget(self._risk_panel)
        main.addLayout(self._confidence_risk_row)

        self._build_section_header(main, "Why This Prediction", "Factor contributions and evidence")
        self._explanation_container = QVBoxLayout()
        self._explanation_container.setContentsMargins(0, 0, 0, 0)
        self._explanation_container.setSpacing(_px8)
        main.addLayout(self._explanation_container)

        self._build_section_header(main, "Reasoning Chain", "Step-by-step inference")
        self._reason_container = QVBoxLayout()
        self._reason_container.setContentsMargins(0, 0, 0, 0)
        self._reason_container.setSpacing(_px8)
        main.addLayout(self._reason_container)

        self._build_section_header(main, "What-If Scenarios", "Compare alternative interventions")
        self._scenario_container = QVBoxLayout()
        self._scenario_container.setContentsMargins(0, 0, 0, 0)
        self._scenario_container.setSpacing(_px8)
        main.addLayout(self._scenario_container)

        main.addStretch()

    def _build_section_header(self, parent: QVBoxLayout, title: str, subtitle: str) -> None:
        header = SectionHeader(title=title, subtitle=subtitle)
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, _px24, 0, _px8)
        hbox.addWidget(header)
        parent.addLayout(hbox)

    def _build_hero(self, parent: QVBoxLayout) -> None:
        colors = self._colors()
        hero = QFrame()
        hero.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.surface};
                border-radius: {R.xl};
                border: 1px solid {colors.border};
            }}
        """)
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(24, 20, 24, 20)
        hero_layout.setSpacing(16)

        accent = QFrame()
        accent.setFixedWidth(4)
        accent.setStyleSheet(f"background-color: {colors.secondary}; border-radius: 2px; border: none;")
        hero_layout.addWidget(accent)

        text_area = QVBoxLayout()
        text_area.setSpacing(6)

        title = QLabel("Predictive Intelligence")
        title.setStyleSheet(f"color: {colors.text_primary}; {font_style('h4')}")
        text_area.addWidget(title)

        self._hero_subtitle = QLabel("Predict your progress, manage risk, and explore what-if scenarios")
        self._hero_subtitle.setStyleSheet(f"color: {colors.text_secondary}; {font_style('body_small')}")
        self._hero_subtitle.setWordWrap(True)
        text_area.addWidget(self._hero_subtitle)

        text_area.addStretch()
        hero_layout.addLayout(text_area, 1)

        self._hero_count_badge = StatusBadge("No Predictions", StatusLevel.NEUTRAL, outlined=True)
        hero_layout.addWidget(self._hero_count_badge)

        parent.addWidget(hero)

    @staticmethod
    def _risk_color(value: float) -> str:
        colors_obj = color_from_scheme(ColorScheme.DARK)
        if value >= 0.7:
            return colors_obj.error
        if value >= 0.4:
            return colors_obj.warning
        return colors_obj.success

    def _make_pred_card(self, title: str, wd: PredictionWidgetData) -> QWidget | None:
        if not wd.has_data:
            return None
        colors = self._colors()
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {colors.surface};
                border-radius: {R.lg};
                border: 1px solid {colors.border};
            }}
            QFrame:hover {{
                border-color: {colors.border_hover};
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        header_row = QHBoxLayout()
        header_row.setSpacing(8)
        lbl = QLabel(title.upper())
        lbl.setStyleSheet(f"color: {colors.text_secondary}; {font_style('label')}; letter-spacing: 0.5px; background: transparent; border: none;")
        header_row.addWidget(lbl)
        header_row.addStretch()

        trend = wd.trend_direction
        trend_icon = "\u2192"
        trend_color = colors.text_disabled
        if trend in ("increasing", "up", "positive"):
            trend_icon = "\u2191"
            trend_color = colors.success
        elif trend in ("decreasing", "down", "negative"):
            trend_icon = "\u2193"
            trend_color = colors.error

        trend_lbl = QLabel(trend_icon)
        trend_lbl.setStyleSheet(f"color: {trend_color}; font-size: 14px; font-weight: 700; background: transparent; border: none;")
        header_row.addWidget(trend_lbl)
        layout.addLayout(header_row)

        val_lbl = QLabel(wd.value)
        val_color = wd.score_color
        val_lbl.setStyleSheet(f"color: {val_color}; {font_style('h3')}; background: transparent; border: none;")
        layout.addWidget(val_lbl)

        prob_lbl = QLabel(f"Probability: {wd.probability}")
        prob_lbl.setStyleSheet(f"color: {colors.text_secondary}; {font_style('body_small')}; background: transparent; border: none;")
        layout.addWidget(prob_lbl)

        conf_lbl = QLabel(wd.confidence)
        conf_lbl.setStyleSheet(f"color: {colors.text_disabled}; {font_style('caption')}; background: transparent; border: none;")
        layout.addWidget(conf_lbl)

        return card

    def refresh(self, data: PredictionDashboardData | None = None) -> None:
        if data is not None:
            self._data = data
        if self._data is None:
            return

        self._clear_grid()
        self._update_hero(self._data)
        self._update_prediction_cards(self._data)
        self._update_timeline(self._data)
        self._update_confidence_risk(self._data)
        self._update_explanation(self._data)
        self._update_reason_chain(self._data)
        self._update_scenarios(self._data)

    def _clear_grid(self) -> None:
        for card in self._pred_cards:
            card.deleteLater()
        self._pred_cards.clear()

    def _update_hero(self, data: PredictionDashboardData) -> None:
        vm = data.view_model
        if data.has_data and vm.has_data:
            self._hero_count_badge.setText(f"{8} Predictions")
            self._hero_count_badge.set_level(StatusLevel.SUCCESS)
        else:
            self._hero_count_badge.setText("No Predictions")
            self._hero_count_badge.set_level(StatusLevel.NEUTRAL)

    def _update_prediction_cards(self, data: PredictionDashboardData) -> None:
        vm = data.view_model
        cards_data = [
            ("PR Probability", vm.pr_prediction),
            ("Plateau Risk", vm.plateau_prediction),
            ("Recovery", vm.recovery_forecast),
            ("Bodyweight", vm.bodyweight_forecast),
            ("Goal ETA", vm.goal_eta),
            ("MRV Risk", vm.mrv_risk),
            ("Deload Risk", vm.deload_probability),
            ("Consistency", vm.consistency_forecast),
        ]
        col = 0
        row = 0
        for title, wd in cards_data:
            card = self._make_pred_card(title, wd)
            if card:
                self._card_grid.addWidget(card, row, col)
                self._pred_cards.append(card)
                col += 1
                if col >= 4:
                    col = 0
                    row += 1

        if not self._pred_cards:
            colors = self._colors()
            empty = QLabel("No prediction data available yet. Complete workouts to generate predictions.")
            empty.setStyleSheet(f"color: {colors.text_disabled}; {font_style('body_small')}")
            empty.setAlignment(Qt.AlignCenter)
            empty.setWordWrap(True)
            self._card_grid.addWidget(empty, 0, 0, 1, 4)
            self._pred_cards.append(empty)

    def _update_timeline(self, data: PredictionDashboardData) -> None:
        vm = data.view_model
        if vm.forecast_timelines and vm.forecast_timelines[0].points:
            self._timeline_chart.show()
            self._timeline_empty.hide()
            tl = vm.forecast_timelines[0]
            points = [(p.date, p.predicted, p.confidence) for p in tl.points]
            self._timeline_chart.set_data(points)
        else:
            self._timeline_chart.hide()
            self._timeline_empty.show()

    def _update_confidence_risk(self, data: PredictionDashboardData) -> None:
        vm = data.view_model
        result = data.result
        colors = self._colors()

        confidences = []
        for attr in ["pr_prediction", "plateau_prediction", "recovery_forecast",
                      "bodyweight_forecast", "goal_eta", "mrv_risk",
                      "deload_probability", "consistency_forecast"]:
            wd = getattr(vm, attr, None)
            if wd and wd.has_data:
                conf_text = wd.confidence
                try:
                    conf_val = float(conf_text.split("(")[1].split("%")[0]) / 100
                    confidences.append(conf_val)
                except (ValueError, IndexError):
                    pass

        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0
        self._confidence_gauge.set_confidence(avg_conf, "Average Prediction Confidence")
        self._confidence_detail.setText(
            f"Based on {len(confidences)} prediction{'s' if len(confidences) != 1 else ''}"
        )

        if result and result.risk_metrics:
            first_key = next(iter(result.risk_metrics))
            rm = result.risk_metrics[first_key]
            self._risk_meter.set_risk(rm.overall_risk_score, f"{rm.risk_level.upper()} Risk")
            self._risk_detail.setText(
                f"Stability: {rm.stability:.0%} \u00b7 "
                f"Sensitivity: {rm.sensitivity:.0%} \u00b7 "
                f"Volatility: {rm.volatility:.0%}"
            )
        else:
            self._risk_meter.set_risk(0.0, "Risk Level")
            self._risk_detail.setText("No risk metrics available")

    def _update_explanation(self, data: PredictionDashboardData) -> None:
        for i in reversed(range(self._explanation_container.count())):
            item = self._explanation_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        result = data.result
        colors = self._colors()

        if not result or not result.explainability:
            empty = QLabel("No explanation data available. Predictions will appear after completing workouts.")
            empty.setStyleSheet(f"color: {colors.text_disabled}; {font_style('body_small')}")
            empty.setAlignment(Qt.AlignCenter)
            empty.setWordWrap(True)
            self._explanation_container.addWidget(empty)
            return

        for key, detail in result.explainability.items():
            if detail.nl_explanation and detail.nl_explanation.short:
                card = InsightCard(
                    icon="\ud83d\udca1",
                    title=detail.nl_explanation.short[:80],
                    description=detail.nl_explanation.detailed[:200] if detail.nl_explanation.detailed else "",
                    badge_text=key,
                    badge_level=StatusLevel.INFO,
                )
                self._explanation_container.addWidget(card)

            if detail.nl_explanation and detail.nl_explanation.actionable:
                action_card = InsightCard(
                    icon="\u2192",
                    title="Recommended Action",
                    description=detail.nl_explanation.actionable,
                    badge_text="Action",
                    badge_level=StatusLevel.SUCCESS,
                )
                self._explanation_container.addWidget(action_card)

            if detail.factor_contributions:
                contrib_panel = SectionPanel(
                    title=f"Key Factors [{key}]",
                    subtitle="Top contributing factors",
                    span=PanelSpan.FULL,
                )
                for fc in detail.factor_contributions[:6]:
                    sign = "+" if fc.direction == "positive" else ""
                    fc_color = colors.success if fc.direction == "positive" else colors.error
                    row = QHBoxLayout()
                    row.setContentsMargins(0, _px4, 0, _px4)
                    fn = QLabel(fc.factor_name)
                    fn.setStyleSheet(f"color: {colors.text_secondary}; {font_style('body_small')}; background: transparent;")
                    row.addWidget(fn, 1)
                    fv = QLabel(f"{sign}{fc.contribution:.2f}")
                    fv.setStyleSheet(f"color: {fc_color}; {font_style('body_small', 'bold')}; background: transparent;")
                    row.addWidget(fv)
                    container = QWidget()
                    container.setLayout(row)
                    contrib_panel.add_content(container)
                self._explanation_container.addWidget(contrib_panel)

            if detail.mr_explanation and detail.mr_explanation.evidence_summary:
                for ev in detail.mr_explanation.evidence_summary[:3]:
                    source = ev.get("source", "Unknown source")[:60]
                    rel = ev.get("relevance", 0)
                    ev_card = InsightCard(
                        icon="\ud83d\udcca",
                        title=f"Evidence: {source}",
                        description=f"Relevance: {rel:.0%}",
                        badge_text="Evidence",
                        badge_level=StatusLevel.NEUTRAL,
                    )
                    self._explanation_container.addWidget(ev_card)

            if detail.mr_explanation and detail.mr_explanation.risk_flags:
                for flag in detail.mr_explanation.risk_flags[:3]:
                    flag_card = InsightCard(
                        icon="\u26a0",
                        title="Risk Flag",
                        description=flag[:160],
                        badge_text="Risk",
                        badge_level=StatusLevel.ERROR,
                    )
                    self._explanation_container.addWidget(flag_card)

    def _update_reason_chain(self, data: PredictionDashboardData) -> None:
        for i in reversed(range(self._reason_container.count())):
            item = self._reason_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        result = data.result
        colors = self._colors()

        if not result or not result.explainability:
            empty = QLabel("No reasoning chain data available.")
            empty.setStyleSheet(f"color: {colors.text_disabled}; {font_style('body_small')}")
            empty.setAlignment(Qt.AlignCenter)
            self._reason_container.addWidget(empty)
            return

        has_chain = False
        for key, detail in result.explainability.items():
            if detail.reason_chain and detail.reason_chain.steps:
                has_chain = True
                chain = detail.reason_chain

                chain_panel = SectionPanel(
                    title=f"Inference Chain [{key}]",
                    subtitle=f"{len(chain.steps)} steps \u00b7 confidence: {chain.overall_confidence:.0%}",
                    span=PanelSpan.FULL,
                )
                for step in chain.steps:
                    step_frame = QFrame()
                    step_frame.setStyleSheet(f"""
                        QFrame {{
                            background-color: transparent;
                            border-left: 2px solid {colors.primary};
                            border-radius: 0px;
                            padding: 0px;
                        }}
                    """)
                    step_layout = QVBoxLayout(step_frame)
                    step_layout.setContentsMargins(_px12, _px6, 0, _px6)
                    step_layout.setSpacing(2)

                    step_header = QHBoxLayout()
                    step_header.setSpacing(8)
                    step_num = QLabel(f"Step {step.step_number}")
                    step_num.setStyleSheet(f"color: {colors.primary}; {font_style('label', 'bold')}; background: transparent;")
                    step_header.addWidget(step_num)
                    step_header.addStretch()
                    step_conf = QLabel(f"confidence: {step.confidence_at_step:.0%}")
                    conf_color = colors.success if step.confidence_at_step >= 0.8 else colors.warning if step.confidence_at_step >= 0.5 else colors.error
                    step_conf.setStyleSheet(f"color: {conf_color}; {font_style('caption')}; background: transparent;")
                    step_header.addWidget(step_conf)
                    step_layout.addLayout(step_header)

                    if step.premise:
                        p = QLabel(f"Premise: {step.premise}")
                        p.setStyleSheet(f"color: {colors.text_secondary}; {font_style('body_small')}; background: transparent;")
                        p.setWordWrap(True)
                        step_layout.addWidget(p)

                    if step.conclusion:
                        c = QLabel(f"\u2192 {step.conclusion}")
                        c.setStyleSheet(f"color: {colors.text_primary}; {font_style('body_small', 'bold')}; background: transparent;")
                        c.setWordWrap(True)
                        step_layout.addWidget(c)

                    chain_panel.add_content(step_frame)

                self._reason_container.addWidget(chain_panel)

        if not has_chain:
            empty = QLabel("No reasoning chain available for current predictions.")
            empty.setStyleSheet(f"color: {colors.text_disabled}; {font_style('body_small')}")
            empty.setAlignment(Qt.AlignCenter)
            self._reason_container.addWidget(empty)

    def _update_scenarios(self, data: PredictionDashboardData) -> None:
        for i in reversed(range(self._scenario_container.count())):
            item = self._scenario_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        result = data.result
        colors = self._colors()

        if not result or not result.scenario_results:
            empty = QLabel("No scenario data available. Predictions are needed to generate what-if comparisons.")
            empty.setStyleSheet(f"color: {colors.text_disabled}; {font_style('body_small')}")
            empty.setAlignment(Qt.AlignCenter)
            empty.setWordWrap(True)
            self._scenario_container.addWidget(empty)
            return

        for sr in result.scenario_results:
            scenario_panel = SectionPanel(
                title=sr.intervention.label,
                subtitle=sr.overall_assessment[:100] if sr.overall_assessment else "",
                span=PanelSpan.FULL,
            )

            badge_text = "\u2714 Recommended" if sr.recommended else "\u2718 Not Recommended"
            badge_level = StatusLevel.SUCCESS if sr.recommended else StatusLevel.ERROR
            badge = StatusBadge(text=badge_text, level=badge_level, outlined=True)
            scenario_panel.add_content(badge)

            risk_badge = StatusBadge(
                text=f"Risk: {sr.risk_level.upper()}",
                level=StatusLevel.WARNING if sr.risk_level in ("high", "moderate") else StatusLevel.SUCCESS,
                outlined=True,
            )
            scenario_panel.add_content(risk_badge)

            if sr.comparisons:
                for comp in sr.comparisons[:3]:
                    delta_str = f"{comp.delta:+.1f} ({comp.delta_percent:+.1f}%)"
                    delta_color = colors.success if comp.is_positive else colors.error
                    row = QHBoxLayout()
                    row.setContentsMargins(0, _px4, 0, _px4)
                    cl = QLabel(comp.intervention.label)
                    cl.setStyleSheet(f"color: {colors.text_secondary}; {font_style('body_small')}; background: transparent;")
                    row.addWidget(cl, 1)
                    cv = QLabel(delta_str)
                    cv.setStyleSheet(f"color: {delta_color}; {font_style('body_small', 'bold')}; background: transparent;")
                    row.addWidget(cv)
                    container = QWidget()
                    container.setLayout(row)
                    scenario_panel.add_content(container)

            self._scenario_container.addWidget(scenario_panel)
