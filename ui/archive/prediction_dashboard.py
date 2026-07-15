"""Prediction Experience 2.0 — decision support, not forecasting.

Layout hierarchy (top-to-bottom, one story):

  ┌──────────────────────────────────────────────────────────┐
  │  HERO                                                    │
  │  One dominant prediction · Confidence · Primary CTA      │
  │  "Expected Bench PR within 3 weeks"                      │
  └──────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────┐
  │  SUMMARY — One natural language paragraph                │
  └──────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────┐
  │  EVIDENCE — Cards proving WHY (Volume, Sleep, Recovery) │
  └──────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────┐
  │  REASONING — Visual inference chain                     │
  └──────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────┐
  │  COUNTERFACTUALS — Premium "What If" scenario cards     │
  └──────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────┐
  │  FORECAST — PredictionTimeline + narrative              │
  └──────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────┐
  │  COACH — Max 3 recommendations                          │
  └──────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────┐
  │  CONFIDENCE — Gauge + explanation of uncertainty        │
  └──────────────────────────────────────────────────────────┘
  ┌──────────────────────────────────────────────────────────┐
  │  ACTION PLAN — Today · This week · Review · CTAs        │
  └──────────────────────────────────────────────────────────┘

Preserved: PredictionDashboardData dataclass, refresh(data) API, same business logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from modules.prediction.domain import PredictionResult
from modules.prediction.presentation import PredictionViewModel
from ui.design_system.components.app_card import AppCard
from ui.design_system.components.chart_container import ChartContainer
from ui.design_system.components.section_header import SectionHeader
from ui.design_system.components.status_badge import StatusBadge, StatusLevel
from ui.design_system.layout import EditorialGrid, PanelSpan, ScrollContainer
from ui.design_system.tokens.color import ColorScheme, color_from_scheme, resolve_alpha
from ui.design_system.tokens.elevation import ElevationTokens, apply_elevation
from ui.design_system.tokens.motion import MotionTokens
from ui.design_system.tokens.radius import RadiusTokens, px_from_token
from ui.design_system.tokens.spacing import SpacingTokens
from ui.design_system.tokens.typography import TypographyTokens, font_style
from ui.design_system.visualization import ConfidenceGauge, PredictionTimeline
from ui.narrative.cards import CoachCardStack
from ui.narrative.engine import Narrative

M = MotionTokens()
S = SpacingTokens()
R = RadiusTokens()
T = TypographyTokens()
E = ElevationTokens()

_pxf = px_from_token
_px4 = _pxf(S.s1)
_px8 = _pxf(S.s2)
_px12 = _pxf(S.s3)
_px16 = _pxf(S.s4)
_px20 = _pxf(S.s5)
_px24 = _pxf(S.s6)
_px32 = _pxf(S.s8)
_px40 = _pxf(S.s10)


# ─── Data Contract ─────────────────────────────────────────────────


@dataclass
class PredictionDashboardData:
    view_model: PredictionViewModel = field(default_factory=PredictionViewModel)
    has_data: bool = False
    result: PredictionResult | None = None


# ─── Helpers ───────────────────────────────────────────────────────


def _confidence_color(pct: float) -> str:
    colors = color_from_scheme(ColorScheme.DARK)
    if pct >= 70:
        return colors.success
    if pct >= 40:
        return colors.warning
    return colors.error


def _predict_emoji(prediction_type: str) -> str:
    """Choose an emoji based on prediction type."""
    mapping = {
        "pr": "\U0001F3CB",
        "plateau": "\U0001F4C9",
        "recovery": "\U0001FA9D",
        "bodyweight": "\U0001F4AA",
        "goal": "\U0001F3AF",
        "mrv": "\u26A0",
        "deload": "\U0001F504",
        "consistency": "\u2714",
    }
    for key, emoji in mapping.items():
        if key in prediction_type.lower():
            return emoji
    return "\U0001F52E"


def _evidence_score(value: float, invert: bool = False) -> tuple[str, str]:
    """Map a value to (label, status_level_key)."""
    if invert:
        if value <= 30:
            return ("Excellent", "success")
        if value <= 50:
            return ("Good", "warning")
        return ("Needs Work", "error")
    if value >= 80:
        return ("Excellent", "success")
    if value >= 60:
        return ("Good", "success")
    if value >= 40:
        return ("Fair", "warning")
    return ("Needs Work", "error")


# ─── Custom Widgets ────────────────────────────────────────────────


class _EvidenceCard(AppCard):
    """Compact evidence card showing a single factor's status."""

    def __init__(self, icon: str, title: str, label: str, detail: str, status: str, parent: QWidget | None = None) -> None:
        super().__init__(title="", elevated=False, parent=parent)
        self.setObjectName("EvidenceCard")
        self.setAccessibleName(f"Evidence: {title}")

        colors = color_from_scheme(ColorScheme.DARK)
        status_colors = {"success": colors.success, "warning": colors.warning, "error": colors.error}
        sc = status_colors.get(status, colors.text_secondary)

        # Clear default body and rebuild
        body = getattr(self, "_body", None)
        if body:
            while body.count():
                item = body.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(_px12)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 24px; background: transparent;")
        row.addWidget(icon_lbl)

        col = QVBoxLayout()
        col.setSpacing(2)

        t = QLabel(title)
        t.setStyleSheet(f"color: {colors.text_secondary}; {font_style('label')}; background: transparent;")
        col.addWidget(t)

        val = QLabel(label)
        val.setStyleSheet(f"color: {sc}; {font_style('h3')}; letter-spacing: -0.02em; background: transparent;")
        col.addWidget(val)

        det = QLabel(detail)
        det.setStyleSheet(f"color: {colors.text_disabled}; {font_style('caption')}; background: transparent;")
        col.addWidget(det)

        row.addLayout(col, 1)
        if body:
            body.addLayout(row)


class _ReasonStep(QFrame):
    """A single step in the inference chain: premise → conclusion."""

    def __init__(self, icon: str, premise: str, conclusion: str, highlight: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("ReasonStep")
        colors = color_from_scheme(ColorScheme.DARK)
        border_color = colors.primary if highlight else colors.border

        self.setStyleSheet(f"""
            QFrame#ReasonStep {{
                background-color: {colors.surface};
                border-radius: {R.lg};
                border: 1px solid {border_color};
            }}
        """)
        if highlight:
            apply_elevation(self, 2, is_dark=True, bg_color=colors.surface)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(_px16, _px12, _px16, _px12)
        layout.setSpacing(_px12)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 22px; background: transparent;")
        layout.addWidget(icon_lbl)

        col = QVBoxLayout()
        col.setSpacing(2)

        p = QLabel(premise)
        p.setStyleSheet(
            f"color: {colors.text_primary}; {font_style('body', weight='semibold')}; background: transparent;"
        )
        p.setWordWrap(True)
        col.addWidget(p)

        arrow = QLabel("\u2192")
        arrow.setStyleSheet(f"color: {colors.primary}; {font_style('body')}; background: transparent;")
        col.addWidget(arrow)

        c = QLabel(conclusion)
        c.setStyleSheet(
            f"color: {colors.text_secondary if not highlight else colors.primary}; "
            f"{font_style('body')}; background: transparent;"
        )
        c.setWordWrap(True)
        col.addWidget(c)

        layout.addLayout(col, 1)


class _CounterfactualCard(AppCard):
    """Premium 'What If' scenario card with impact preview."""

    def __init__(
        self, icon: str, action: str, impact: str, impact_pct: float,
        conf_text: str, parent: QWidget | None = None,
    ) -> None:
        super().__init__(title="", elevated=True, parent=parent)
        self.setObjectName("CounterfactualCard")
        self.setAccessibleName(f"What if: {action}")

        colors = color_from_scheme(ColorScheme.DARK)
        impact_color = colors.success if impact_pct >= 0.5 else colors.warning

        # Clear default body
        body = getattr(self, "_body", None)
        if body:
            while body.count():
                item = body.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        # Icon + action
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(_px8)

        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("font-size: 24px; background: transparent;")
        row.addWidget(icon_lbl)

        col = QVBoxLayout()
        col.setSpacing(2)

        what_if = QLabel("What if...")
        what_if.setStyleSheet(f"color: {colors.text_disabled}; {font_style('caption')}; background: transparent;")
        col.addWidget(what_if)

        action_lbl = QLabel(action)
        action_lbl.setStyleSheet(f"color: {colors.text_primary}; {font_style('body', weight='semibold')}; background: transparent;")
        action_lbl.setWordWrap(True)
        col.addWidget(action_lbl)

        row.addLayout(col, 1)
        if body:
            body.addLayout(row)

        # Impact value
        impact_lbl = QLabel(impact)
        impact_lbl.setStyleSheet(f"color: {impact_color}; {font_style('h3')}; background: transparent;")
        if body:
            body.addWidget(impact_lbl)

        # Confidence bar
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(int(impact_pct * 100))
        bar.setTextVisible(False)
        bar.setFixedHeight(6)
        bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {colors.surface_hover};
                border-radius: 3px;
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {resolve_alpha(impact_color, 0.6)};
                border-radius: 3px;
            }}
        """)
        if body:
            body.addWidget(bar)

        conf_lbl = QLabel(conf_text)
        conf_lbl.setStyleSheet(f"color: {colors.text_disabled}; {font_style('caption')}; background: transparent;")
        if body:
            body.addWidget(conf_lbl)


# ─── Prediction Dashboard ─────────────────────────────────────────


class PredictionDashboard(QWidget):
    """Decision-support prediction experience. Answers: 'What should I do next?'"""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _colors(self):
        return color_from_scheme(ColorScheme.DARK)

    # ── Build UI ─────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setStyleSheet("PredictionDashboard { background: transparent; }")
        self._scroll = ScrollContainer()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self._scroll)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._scroll.content_layout.insertLayout(0, layout)

        main = QVBoxLayout()
        main.setContentsMargins(0, 0, _px32, _px40)
        main.setSpacing(0)
        layout.insertLayout(0, main)

        # 1. Hero
        self._build_hero(main)

        main.addSpacing(_px32)

        # 2. Summary
        self._build_section_header(main, "Summary", "What the data says")
        self._summary_card = AppCard(title="", elevated=True)
        main.addWidget(self._summary_card)

        main.addSpacing(_px24)

        # 3. Evidence
        self._build_section_header(main, "Evidence", "Why this prediction")
        self._evidence_grid = EditorialGrid()
        self._evidence_grid.set_spacing(_px16)
        main.addWidget(self._evidence_grid)
        self._evidence_cards: list[_EvidenceCard] = []

        main.addSpacing(_px24)

        # 4. Reasoning
        self._build_section_header(main, "Reasoning", "How we got here")
        self._reasoning_container = QVBoxLayout()
        self._reasoning_container.setContentsMargins(0, 0, 0, 0)
        self._reasoning_container.setSpacing(_px8)
        main.addLayout(self._reasoning_container)

        main.addSpacing(_px24)

        # 5. Counterfactuals
        self._build_section_header(main, "What If\u2026", "Small changes, big impact")
        self._counterfactual_grid = EditorialGrid()
        self._counterfactual_grid.set_spacing(_px16)
        main.addWidget(self._counterfactual_grid)

        main.addSpacing(_px24)

        # 6. Forecast Timeline
        self._build_section_header(main, "Forecast Timeline", "Projected progression")
        self._forecast_container = QVBoxLayout()
        self._forecast_container.setContentsMargins(0, 0, 0, 0)
        self._forecast_container.setSpacing(_px8)
        main.addLayout(self._forecast_container)

        main.addSpacing(_px24)

        # 7. Coach
        self._build_section_header(main, "Coach", "Personalised recommendations")
        self._coach_stack = CoachCardStack()
        main.addWidget(self._coach_stack)

        main.addSpacing(_px24)

        # 8. Confidence
        self._build_section_header(main, "Confidence", "How certain we are")
        self._confidence_card = AppCard(title="", elevated=True)
        main.addWidget(self._confidence_card)

        main.addSpacing(_px24)

        # 9. Action Plan
        self._build_section_header(main, "Action Plan", "What to do next")
        self._action_card = AppCard(title="", elevated=True)
        main.addWidget(self._action_card)

        main.addStretch()

    def _build_section_header(self, parent: QVBoxLayout, title: str, subtitle: str) -> None:
        header = SectionHeader(title=title, subtitle=subtitle)
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, _px8)
        hbox.addWidget(header)
        parent.addLayout(hbox)

    # ── Hero ──────────────────────────────────────────────────────

    def _build_hero(self, parent: QVBoxLayout) -> None:
        colors = self._colors()

        self._hero_frame = QFrame()
        self._hero_frame.setObjectName("PredictionHero")
        self._hero_frame.setMinimumHeight(240)
        self._hero_frame.setStyleSheet(f"""
            QFrame#PredictionHero {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(12,16,51,200), stop:0.35 rgba(20,16,74,180),
                    stop:0.7 rgba(26,13,68,160), stop:1 rgba(10,14,40,120));
                border-radius: {R.xl};
                border: 1px solid {resolve_alpha(colors.primary, 0.10)};
            }}
        """)
        apply_elevation(self._hero_frame, 3, is_dark=True, bg_color=colors.surface)

        hero_layout = QHBoxLayout(self._hero_frame)
        hero_layout.setContentsMargins(_px32, _px24, _px32, _px24)
        hero_layout.setSpacing(_px24)

        # Left: prediction info
        left = QVBoxLayout()
        left.setSpacing(_px8)

        self._hero_emoji = QLabel("\U0001F52E")
        self._hero_emoji.setStyleSheet("font-size: 36px; background: transparent;")
        left.addWidget(self._hero_emoji)

        self._hero_title = QLabel("No Prediction Yet")
        self._hero_title.setStyleSheet(
            f"color: {colors.text_primary}; {font_style('h2')}; "
            f"letter-spacing: -0.02em; background: transparent;"
        )
        self._hero_title.setWordWrap(True)
        left.addWidget(self._hero_title)

        self._hero_sub = QLabel("")
        self._hero_sub.setStyleSheet(
            f"color: {colors.text_secondary}; {font_style('body')}; background: transparent;"
        )
        self._hero_sub.setWordWrap(True)
        left.addWidget(self._hero_sub)

        # Confidence row
        conf_row = QHBoxLayout()
        conf_row.setSpacing(_px12)
        conf_row.setContentsMargins(0, _px4, 0, 0)

        self._hero_conf_badge = StatusBadge("--", StatusLevel.NEUTRAL, outlined=True)
        conf_row.addWidget(self._hero_conf_badge)

        self._hero_conf_bar = QProgressBar()
        self._hero_conf_bar.setRange(0, 100)
        self._hero_conf_bar.setValue(0)
        self._hero_conf_bar.setTextVisible(False)
        self._hero_conf_bar.setFixedHeight(8)
        self._hero_conf_bar.setFixedWidth(200)
        self._hero_conf_bar.setStyleSheet(f"""
            QProgressBar {{ background-color: {colors.surface_hover}; border-radius: 4px; border: none; }}
            QProgressBar::chunk {{ border-radius: 4px; }}
        """)
        conf_row.addWidget(self._hero_conf_bar)

        self._hero_conf_pct = QLabel("")
        self._hero_conf_pct.setStyleSheet(
            f"color: {colors.text_disabled}; {font_style('caption', 'bold')}; background: transparent;"
        )
        conf_row.addWidget(self._hero_conf_pct)

        conf_row.addStretch()
        left.addLayout(conf_row)

        hero_layout.addLayout(left, 1)

        # Right: CTA
        right = QVBoxLayout()
        right.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        right.setSpacing(_px8)

        self._hero_cta = QPushButton("  \u25B6  Continue Program")
        self._hero_cta.setAccessibleName("Prediction action: Continue Program")
        self._hero_cta.setFocusPolicy(Qt.StrongFocus)
        self._hero_cta.setCursor(Qt.PointingHandCursor)
        self._hero_cta.setMinimumHeight(48)
        self._hero_cta.setMinimumWidth(200)
        self._hero_cta.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(124,58,237,0.95), stop:0.5 rgba(147,51,234,0.9), stop:1 rgba(192,38,211,0.85));
                color: white;
                border-radius: {R.size_2xl};
                padding: 0 {S.s7};
                {font_style('body', 'bold')}
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(139,92,246,0.95), stop:0.5 rgba(167,139,250,0.9), stop:1 rgba(192,132,252,0.85));
            }}
            QPushButton:focus {{
                border: 2px solid {colors.focus_ring};
            }}
        """)
        right.addWidget(self._hero_cta)

        self._hero_cta_sub = QLabel("Based on current training data")
        self._hero_cta_sub.setStyleSheet(
            f"color: {colors.text_disabled}; {font_style('caption')}; background: transparent;"
        )
        self._hero_cta_sub.setAlignment(Qt.AlignRight)
        right.addWidget(self._hero_cta_sub)

        hero_layout.addLayout(right)

        parent.addWidget(self._hero_frame)

    # ── Refresh ──────────────────────────────────────────────────

    def refresh(self, data: PredictionDashboardData | None = None) -> None:
        if data is None:
            return
        self._clear_all()
        self._update_hero(data)
        self._update_summary(data)
        self._update_evidence(data)
        self._update_reasoning(data)
        self._update_counterfactuals(data)
        self._update_forecast(data)
        self._update_coach(data)
        self._update_confidence(data)
        self._update_action_plan(data)

    def _clear_all(self) -> None:
        """Clear dynamic content containers before rebuild."""
        for card in self._evidence_cards:
            card.deleteLater()
        self._evidence_cards.clear()
        self._clear_card_body(self._summary_card)
        self._clear_card_body(self._confidence_card)
        self._clear_card_body(self._action_card)
        self._clear_layout(self._reasoning_container)
        self._clear_layout(self._forecast_container)
        self._counterfactual_grid.clear()
        self._coach_stack.clear()

    # ── Update: Hero ─────────────────────────────────────────────

    def _update_hero(self, data: PredictionDashboardData) -> None:
        colors = self._colors()
        vm = data.view_model
        result = data.result

        if not data.has_data or not vm.has_data:
            self._hero_emoji.setText("\U0001F52E")
            self._hero_title.setText("No Predictions Yet")
            self._hero_sub.setText("Complete more workouts to unlock personalised predictions. GymOS will analyse your training patterns to forecast progress.")
            self._hero_conf_badge.setText("--")
            self._hero_conf_badge.set_level(StatusLevel.NEUTRAL)
            self._hero_conf_bar.setValue(0)
            self._hero_conf_bar.setStyleSheet(f"""
                QProgressBar {{ background-color: {colors.surface_hover}; border-radius: 4px; border: none; }}
                QProgressBar::chunk {{ border-radius: 4px; background-color: {colors.text_disabled}; }}
            """)
            self._hero_conf_pct.setText("")
            self._hero_cta.setText("  \u25B6  Start Training")
            self._hero_cta_sub.setText("First prediction after 3+ workouts")
            return

        # Find the best prediction to feature
        best_pred = self._find_best_prediction(vm, result)
        if best_pred is None:
            # Show a generic prediction overview
            count = sum(1 for attr in [
                "pr_prediction", "plateau_prediction", "recovery_forecast",
                "bodyweight_forecast", "goal_eta", "mrv_risk",
                "deload_probability", "consistency_forecast",
            ] if getattr(vm, attr, None) and getattr(vm, attr).has_data)

            self._hero_emoji.setText("\U0001F52E")
            self._hero_title.setText(f"{count} Predictions Available")
            self._hero_sub.setText("Review the sections below for detailed forecasts across your training metrics.")
            self._hero_conf_badge.setText("Active")
            self._hero_conf_badge.set_level(StatusLevel.INFO)
            self._hero_conf_bar.setValue(50)
            self._hero_conf_bar.setStyleSheet(f"""
                QProgressBar {{ background-color: {colors.surface_hover}; border-radius: 4px; border: none; }}
                QProgressBar::chunk {{ border-radius: 4px; background-color: {colors.info}; }}
            """)
            self._hero_conf_pct.setText("")
            self._hero_cta.setText("  \u25B6  Review Predictions")
            self._hero_cta_sub.setText("Scroll down for detailed analysis")
            return

        # Show the best prediction in hero
        title, emoji, value_str, conf_score, conf_level, narrative = best_pred

        self._hero_emoji.setText(emoji)
        self._hero_title.setText(title)
        self._hero_sub.setText(narrative)

        conf_pct = conf_score * 100
        conf_color = _confidence_color(conf_pct)
        self._hero_conf_badge.setText(conf_level)
        status_map = {"Very High": StatusLevel.SUCCESS, "High": StatusLevel.SUCCESS,
                      "Moderate": StatusLevel.WARNING, "Low": StatusLevel.WARNING,
                      "Very Low": StatusLevel.ERROR}
        self._hero_conf_badge.set_level(status_map.get(conf_level, StatusLevel.NEUTRAL))
        self._hero_conf_bar.setValue(int(conf_pct))
        self._hero_conf_bar.setStyleSheet(f"""
            QProgressBar {{ background-color: {colors.surface_hover}; border-radius: 4px; border: none; }}
            QProgressBar::chunk {{ border-radius: 4px; background-color: {conf_color}; }}
        """)
        self._hero_conf_pct.setText(f"{conf_pct:.0f}%")
        self._hero_cta.setText("  \u25B6  Continue Program")
        self._hero_cta_sub.setText(f"Confidence: {conf_level} · {value_str}")

    def _find_best_prediction(self, vm: PredictionViewModel, result: PredictionResult | None) -> tuple | None:
        """Find the most confident prediction with data for hero display."""
        candidates = []

        # Check all 8 prediction types
        checks = [
            ("pr_prediction", "Expected PR", "\U0001F3CB"),
            ("plateau_prediction", "Plateau Risk", "\U0001F4C9"),
            ("recovery_forecast", "Recovery Forecast", "\U0001FA9D"),
            ("bodyweight_forecast", "Bodyweight Trend", "\U0001F4AA"),
            ("goal_eta", "Goal ETA", "\U0001F3AF"),
            ("mrv_risk", "MRV Risk", "\u26A0"),
            ("deload_probability", "Deload Risk", "\U0001F504"),
            ("consistency_forecast", "Consistency Forecast", "\u2714"),
        ]

        for attr, label, emoji in checks:
            wd = getattr(vm, attr, None)
            if wd and wd.has_data:
                conf_text = wd.confidence
                conf_score = 0.5
                conf_level = "Moderate"
                try:
                    if "%" in conf_text:
                        conf_pct = float(conf_text.split("(")[1].split("%")[0]) if "(" in conf_text else float(conf_text.split("%")[0])
                        conf_score = conf_pct / 100.0
                    conf_level = conf_text.split("(")[0].strip() if "(" in conf_text else conf_text
                except (ValueError, IndexError):
                    pass

                narrative = wd.summary or f"{label}: {wd.value}"
                candidates.append((
                    f"{label}: {wd.value}",
                    emoji,
                    wd.value,
                    conf_score,
                    conf_level,
                    narrative,
                ))

        if not candidates:
            return None

        # Pick the one with highest confidence score
        candidates.sort(key=lambda c: c[3], reverse=True)
        return candidates[0]

    # ── Update: Summary ──────────────────────────────────────────

    def _update_summary(self, data: PredictionDashboardData) -> None:
        colors = self._colors()
        vm = data.view_model

        if not data.has_data or not vm.has_data:
            empty = QLabel("Complete workouts to receive personalised prediction summaries. GymOS will analyse your training progression, recovery trends, and consistency patterns to forecast your next milestones.")
            empty.setStyleSheet(
                f"color: {colors.text_disabled}; {font_style('body')}; background: transparent;"
            )
            empty.setWordWrap(True)
            empty.setAlignment(Qt.AlignCenter)
            self._summary_card.add_content(empty)
            return

        # Build a natural language summary from available predictions
        parts = []
        pr = vm.pr_prediction
        plateau = vm.plateau_prediction
        recovery = vm.recovery_forecast
        bodyweight = vm.bodyweight_forecast
        consistency = vm.consistency_forecast

        if pr and pr.has_data:
            parts.append(
                f"Current progression indicates a {pr.probability} probability "
                f"of reaching your next performance milestone."
            )
        if recovery and recovery.has_data:
            parts.append(f"Recovery quality has been {recovery.value.lower()}.")
        if consistency and consistency.has_data:
            parts.append(
                f"Training consistency is {consistency.trend_direction.lower()}, "
                f"supporting continued progress."
            )
        if plateau and plateau.has_data:
            parts.append(f"Plateau risk is {plateau.value.lower()}.")
        if bodyweight and bodyweight.has_data:
            parts.append(f"Bodyweight is trending {bodyweight.trend_direction.lower()}.")

        if not parts:
            summary_text = "Predictions are being calculated. Check back after your next few workouts."
        else:
            summary_text = " ".join(parts)

        summary_lbl = QLabel(summary_text)
        summary_lbl.setStyleSheet(
            f"color: {colors.text_secondary}; {font_style('body')}; background: transparent;"
        )
        summary_lbl.setWordWrap(True)
        self._summary_card.add_content(summary_lbl)

    # ── Update: Evidence ─────────────────────────────────────────

    def _update_evidence(self, data: PredictionDashboardData) -> None:
        colors = self._colors()
        vm = data.view_model

        # Clear existing evidence cards
        for card in self._evidence_cards:
            card.deleteLater()
        self._evidence_cards.clear()

        # Derive evidence factors from available data
        evidence_list = []

        # Volume evidence (from MRV or volume prediction)
        mrv = vm.mrv_risk
        if mrv and mrv.has_data:
            try:
                vol_val = float(mrv.value.split()[0]) if mrv.value else 0
            except (ValueError, IndexError):
                vol_val = 0
            trend = mrv.trend_direction
            vol_label, vol_status = _evidence_score(abs(vol_val))
            vol_detail = f"{trend.capitalize()} · {mrv.value}" if trend else mrv.value
            evidence_list.append(("\U0001F4C8", "Training Volume", vol_label, vol_detail, vol_status))

        # Sleep evidence (from recovery forecast)
        recovery = vm.recovery_forecast
        if recovery and recovery.has_data:
            sleep_label, sleep_status = _evidence_score(70 if recovery.trend_direction in ("increasing", "stable") else 45)
            sleep_detail = f"{recovery.trend_direction.capitalize()} · {recovery.value}"
            evidence_list.append(("\U0001F634", "Sleep & Recovery", sleep_label, sleep_detail, sleep_status))

        # Recovery/Readiness evidence
        if recovery and recovery.has_data:
            try:
                rec_val = float(recovery.value.split("/")[0]) if "/" in recovery.value else 70
            except (ValueError, IndexError):
                rec_val = 70
            rec_label, rec_status = _evidence_score(rec_val)
            evidence_list.append(("\U0001F6E1", "Recovery", rec_label, f"Score: {recovery.value}", rec_status))

        # Consistency evidence
        consistency = vm.consistency_forecast
        if consistency and consistency.has_data:
            cons_label, cons_status = _evidence_score(
                80 if consistency.trend_direction in ("stable", "increasing") else 40
            )
            cons_detail = f"{consistency.trend_direction.capitalize()} · {consistency.value}"
            evidence_list.append(("\u2714", "Consistency", cons_label, cons_detail, cons_status))

        # Progressive overload evidence
        pr = vm.pr_prediction
        if pr and pr.has_data:
            ol_label = "Excellent" if pr.trend_direction in ("increasing", "positive") else "Good" if pr.trend_direction == "stable" else "Needs Work"
            ol_status = "success" if ol_label == "Excellent" else "warning" if ol_label == "Good" else "error"
            evidence_list.append(("\U0001F4CB", "Progressive Overload", ol_label, pr.trend_direction.capitalize(), ol_status))

        if not evidence_list:
            # Empty state
            empty_card = AppCard(title="", elevated=False)
            empty_lbl = QLabel("No evidence available yet. Complete workouts to build prediction data.")
            empty_lbl.setStyleSheet(
                f"color: {colors.text_disabled}; {font_style('body_small')}; background: transparent;"
            )
            empty_lbl.setWordWrap(True)
            empty_lbl.setAlignment(Qt.AlignCenter)
            empty_card.add_content(empty_lbl)
            self._evidence_grid.add_panel(empty_card, span=PanelSpan.FULL)
            self._evidence_cards.append(empty_card)
            return

        for icon, title, label, detail, status in evidence_list[:4]:
            card = _EvidenceCard(icon, title, label, detail, status)
            self._evidence_cards.append(card)
            self._evidence_grid.add_panel(card, span=PanelSpan.QUARTER)

    # ── Update: Reasoning ────────────────────────────────────────

    def _update_reasoning(self, data: PredictionDashboardData) -> None:
        colors = self._colors()
        vm = data.view_model

        if not data.has_data or not vm.has_data:
            empty = QLabel("Complete workouts to unlock the reasoning chain behind your predictions.")
            empty.setStyleSheet(
                f"color: {colors.text_disabled}; {font_style('body_small')}; background: transparent;"
            )
            empty.setWordWrap(True)
            empty.setAlignment(Qt.AlignCenter)
            self._reasoning_container.addWidget(empty)
            return

        # Build reasoning steps from prediction data
        steps = []

        # Step 1: Training Volume
        mrv = vm.mrv_risk
        if mrv and mrv.has_data:
            vol_narrative = f"Volume is {mrv.trend_direction.lower()}"
            if mrv.value:
                vol_narrative += f" ({mrv.value})"
            steps.append(("\U0001F4C8", f"Training Volume \u2014 {vol_narrative}", "Creates adaptation stimulus for muscle growth and strength.", False))

        # Step 2: Recovery
        recovery = vm.recovery_forecast
        if recovery and recovery.has_data:
            rec_narrative = f"Recovery is {recovery.trend_direction.lower()} ({recovery.value})"
            steps.append(("\U0001F6E1", rec_narrative, "Enables muscle repair and nervous system recovery between sessions.", False))

        # Step 3: Consistency
        consistency = vm.consistency_forecast
        if consistency and consistency.has_data:
            cons_narrative = f"Consistency is {consistency.trend_direction.lower()}"
            if consistency.value:
                cons_narrative += f" ({consistency.value})"
            steps.append(("\u2714", cons_narrative, "Sustained training frequency drives long-term strength adaptations.", False))

        # Step 4: Expected Strength Gain (from PR prediction)
        pr = vm.pr_prediction
        if pr and pr.has_data:
            pr_narrative = f"Strength progression suggests {pr.value} probability of PR"
            steps.append(("\U0001F4AA", pr_narrative, "Expected strength gain based on volume, recovery, and consistency.", True))

        # Step 5: Predicted PR (highlighted)
        if pr and pr.has_data:
            steps.append(("\U0001F3C6", f"Predicted Outcome \u2014 {pr.probability} chance", pr.summary or "PR within forecast window based on current trajectory.", True))
        elif steps:
            # Generic final step
            steps.append(("\U0001F3C6", "Predicted Outcome", "Continued progression expected with current training approach.", True))

        if not steps:
            empty = QLabel("Reasoning chain will populate after more training data is collected.")
            empty.setStyleSheet(
                f"color: {colors.text_disabled}; {font_style('body_small')}; background: transparent;"
            )
            empty.setWordWrap(True)
            empty.setAlignment(Qt.AlignCenter)
            self._reasoning_container.addWidget(empty)
            return

        for icon, premise, conclusion, highlight in steps:
            step = _ReasonStep(icon, premise, conclusion, highlight)
            self._reasoning_container.addWidget(step)

    # ── Update: Counterfactuals ──────────────────────────────────

    def _update_counterfactuals(self, data: PredictionDashboardData) -> None:
        self._counterfactual_grid.clear()
        self._colors()
        result = data.result

        if not data.has_data:
            return

        # Try to use real counterfactual results from engine
        cf_results = result.counterfactual_results if result else []
        cards_added = 0

        if cf_results:
            for cf in cf_results[:3]:
                delta = cf.absolute_delta
                impact_pct = min(abs(delta) / 20.0, 1.0) if abs(delta) > 0 else 0.3
                impact_str = f"{'+' if delta > 0 else ''}{delta:.1f} points"
                conf_text = f"Impact: {'High' if impact_pct > 0.6 else 'Moderate' if impact_pct > 0.3 else 'Low'}"

                # Map type to emoji
                type_emoji = {
                    "sleep": "\U0001F634", "calories": "\U0001F35D",
                    "workout_miss": "\U0001F4C5", "volume_change": "\U0001F4C9",
                    "deload_now": "\U0001F504",
                }.get(cf.query.cf_type.value if hasattr(cf.query.cf_type, 'value') else str(cf.query.cf_type).lower(), "\U0001F52E")

                type_label = cf.query.cf_type.label if hasattr(cf.query.cf_type, 'label') else str(cf.query.cf_type).replace("_", " ").title()

                card = _CounterfactualCard(
                    icon=type_emoji,
                    action=type_label,
                    impact=impact_str,
                    impact_pct=impact_pct,
                    conf_text=conf_text,
                )
                self._counterfactual_grid.add_panel(card, span=PanelSpan.THIRD)
                cards_added += 1

        if cards_added == 0:
            # Fall back to default scenarios based on prediction state

            defaults = [
                ("\U0001F634", "Sleep +1 hour", "Confidence +6%", 0.85, "Impact: High"),
            ]
            defaults.append(("\U0001F4C5", "No missed sessions", "PR predicted 5 days sooner", 0.65, "Impact: Moderate"))
            defaults.append(("\U0001F4A7", "Increase hydration", "Recovery +4 points", 0.40, "Impact: Low"))

            for icon, action, impact, pct, conf_text in defaults:
                card = _CounterfactualCard(icon, action, impact, pct, conf_text)
                self._counterfactual_grid.add_panel(card, span=PanelSpan.THIRD)
                cards_added += 1

    # ── Update: Forecast ─────────────────────────────────────────

    def _update_forecast(self, data: PredictionDashboardData) -> None:
        colors = self._colors()
        vm = data.view_model

        has_timeline = vm.forecast_timelines and len(vm.forecast_timelines) > 0 and vm.forecast_timelines[0].points

        if has_timeline:
            # Wrap in ChartContainer
            cc = ChartContainer(title="Forecast Timeline", subtitle="Projected trend over time")
            timeline = PredictionTimeline()
            tl = vm.forecast_timelines[0]
            points = [(p.date, p.predicted, p.confidence) for p in tl.points]
            timeline.set_data(points)
            if hasattr(cc, 'set_widget'):
                cc.set_widget(timeline)
                self._forecast_container.addWidget(cc)
            else:
                self._forecast_container.addWidget(timeline)

            # Narrative below
            window = tl.window_label or "forecast window"
            narrative = (
                f"Expected progression over {window}. "
                f"Confidence decreases further in the future due to increasing uncertainty."
            )
            nav_lbl = QLabel(narrative)
            nav_lbl.setStyleSheet(
                f"color: {colors.text_secondary}; {font_style('body')}; background: transparent;"
            )
            nav_lbl.setWordWrap(True)
            nav_lbl.setAlignment(Qt.AlignCenter)
            self._forecast_container.addWidget(nav_lbl)
        else:
            empty = QLabel("Forecast timeline will appear here after completing more workouts. GymOS needs 3+ sessions to establish a predictive baseline.")
            empty.setStyleSheet(
                f"color: {colors.text_disabled}; {font_style('body_small')}; background: transparent;"
            )
            empty.setWordWrap(True)
            empty.setAlignment(Qt.AlignCenter)
            self._forecast_container.addWidget(empty)

    # ── Update: Coach ────────────────────────────────────────────

    def _update_coach(self, data: PredictionDashboardData) -> None:
        self._coach_stack.clear()
        vm = data.view_model

        if not data.has_data or not vm.has_data:
            self._coach_stack.add_card(Narrative(
                title="Coach Is Waiting",
                summary="Complete more workouts to receive personalised coaching recommendations based on your prediction data.",
                body="GymOS will analyse your progression patterns, recovery trends, and consistency to provide actionable guidance.",
                metadata={"severity": "info"},
            ))
            return

        cards_added = 0

        # Recommendation 1: Based on primary prediction
        pr = vm.pr_prediction
        if pr and pr.has_data and cards_added < 3:
            try:
                prob = float(pr.probability.replace("%", ""))
            except (ValueError, AttributeError):
                prob = 50
            if prob >= 60:
                msg = f"Continue your current program. Progression is on track with {pr.probability} probability of hitting your next PR. Maintain RIR 1-2 on working sets."
                sev = "success"
            elif prob >= 30:
                msg = f"Minor adjustments may help. PR probability is {pr.probability}. Consider reviewing your progression scheme or deload timing."
                sev = "info"
            else:
                msg = f"PR probability is currently {pr.probability}. Consider a program review or deload to reset progression."
                sev = "warning"

            self._coach_stack.add_card(Narrative(
                title="Training Recommendation",
                summary=msg,
                metadata={"severity": sev},
            ))
            cards_added += 1

        # Recommendation 2: Recovery-based
        recovery = vm.recovery_forecast
        if recovery and recovery.has_data and cards_added < 3:
            rec_msg = (
                "Prioritise recovery this week. "
                "Aim for 8 hours of sleep \u2014 each hour correlates with improved readiness."
            )
            self._coach_stack.add_card(Narrative(
                title="Recovery Focus",
                summary=rec_msg,
                metadata={"severity": "info"},
            ))
            cards_added += 1

        # Recommendation 3: Consistency or plateau-based
        consistency = vm.consistency_forecast
        plateau = vm.plateau_prediction
        if consistency and consistency.has_data and cards_added < 3:
            cons_msg = (
                f"Your training consistency is {consistency.trend_direction.lower()}. "
                f"Maintaining a regular schedule is the strongest predictor of long-term progress."
            )
            self._coach_stack.add_card(Narrative(
                title="Consistency Tip",
                summary=cons_msg,
                metadata={"severity": "success"},
            ))
            cards_added += 1
        elif plateau and plateau.has_data and cards_added < 3:
            plat_msg = f"Plateau risk is {plateau.value.lower()}. Consider varying exercise selection or rep schemes to maintain progress."
            self._coach_stack.add_card(Narrative(
                title="Plateau Prevention",
                summary=plat_msg,
                metadata={"severity": "warning"},
            ))
            cards_added += 1

        if cards_added == 0:
            self._coach_stack.add_card(Narrative(
                title="On Track",
                summary="Keep training consistently. Recommendations will become more specific as more data is collected.",
                metadata={"severity": "success"},
            ))

    # ── Update: Confidence ───────────────────────────────────────

    def _update_confidence(self, data: PredictionDashboardData) -> None:
        colors = self._colors()
        vm = data.view_model
        result = data.result

        if not data.has_data or not vm.has_data:
            empty = QLabel("Confidence data will appear after completing workouts. More data = more confident predictions.")
            empty.setStyleSheet(
                f"color: {colors.text_disabled}; {font_style('body_small')}; background: transparent;"
            )
            empty.setWordWrap(True)
            empty.setAlignment(Qt.AlignCenter)
            self._confidence_card.add_content(empty)
            return

        # Calculate average confidence across all predictions
        confidences = []
        for attr in ["pr_prediction", "plateau_prediction", "recovery_forecast",
                      "bodyweight_forecast", "goal_eta", "mrv_risk",
                      "deload_probability", "consistency_forecast"]:
            wd = getattr(vm, attr, None)
            if wd and wd.has_data:
                conf_text = wd.confidence
                try:
                    if "(" in conf_text:
                        conf_val = float(conf_text.split("(")[1].split("%")[0]) / 100.0
                    elif "%" in conf_text:
                        conf_val = float(conf_text.split("%")[0]) / 100.0
                    else:
                        conf_val = 0.5
                    confidences.append(conf_val)
                except (ValueError, IndexError):
                    pass

        avg_conf = sum(confidences) / len(confidences) if confidences else 0.5
        conf_pct = avg_conf * 100

        # Confidence gauge
        gauge = ConfidenceGauge(width=280, height=40)
        gauge.set_confidence(avg_conf, "Average Prediction Confidence")
        self._confidence_card.add_content(gauge)

        # Level + percentage
        level_label = "Very High" if conf_pct >= 80 else "High" if conf_pct >= 60 else "Moderate" if conf_pct >= 40 else "Low" if conf_pct >= 20 else "Very Low"
        level_status = StatusLevel.SUCCESS if conf_pct >= 60 else StatusLevel.WARNING if conf_pct >= 40 else StatusLevel.ERROR
        level_badge = StatusBadge(text=f"{level_label} ({conf_pct:.0f}%)", level=level_status, outlined=False)
        self._confidence_card.add_content(level_badge)

        # Explanation of uncertainty
        reasons = []

        # Check sample size
        sample_sizes = []
        for pred in result.predictions if result else []:
            if pred.confidence and pred.confidence.sample_size > 0:
                sample_sizes.append(pred.confidence.sample_size)
        total_samples = sum(sample_sizes) if sample_sizes else 0

        if total_samples < 5:
            reasons.append(f"Limited data: {total_samples} workouts analyzed")
        else:
            reasons.append(f"Good data foundation: {total_samples} workouts analyzed")

        # Check prediction count
        active_count = sum(1 for attr in [
            "pr_prediction", "plateau_prediction", "recovery_forecast",
            "bodyweight_forecast", "goal_eta", "mrv_risk",
            "deload_probability", "consistency_forecast",
        ] if getattr(vm, attr, None) and getattr(vm, attr).has_data)

        reasons.append(f"Active predictions: {active_count}/8")

        # General uncertainty notes
        if conf_pct < 60:
            reasons.append("Confidence will improve as more training data accumulates")
        elif conf_pct >= 80:
            reasons.append("Strong confidence \u2014 prediction models have sufficient data")

        for reason in reasons:
            rl = QLabel(f"\u2022 {reason}")
            rl.setStyleSheet(
                f"color: {colors.text_secondary}; {font_style('body')}; background: transparent;"
            )
            rl.setWordWrap(True)
            self._confidence_card.add_content(rl)

    # ── Update: Action Plan ──────────────────────────────────────

    def _update_action_plan(self, data: PredictionDashboardData) -> None:
        colors = self._colors()
        vm = data.view_model

        if not data.has_data or not vm.has_data:
            empty = QLabel("An action plan will be generated after completing 3+ workouts.")
            empty.setStyleSheet(
                f"color: {colors.text_disabled}; {font_style('body_small')}; background: transparent;"
            )
            empty.setWordWrap(True)
            empty.setAlignment(Qt.AlignCenter)
            self._action_card.add_content(empty)
            return

        # Today's action
        pr = vm.pr_prediction
        recovery = vm.recovery_forecast
        plateau = vm.plateau_prediction

        today_action = "Complete your next scheduled workout"
        if pr and pr.has_data:
            try:
                prob = float(pr.probability.replace("%", ""))
            except (ValueError, AttributeError):
                prob = 50
            if prob >= 60:
                today_action = "Push for PR attempts in your working sets"
            elif prob >= 30:
                today_action = "Focus on quality reps at RIR 1-2"
            else:
                today_action = "Consider a light session or technique focus"

        this_week_action = "Maintain RIR 1-2 on working sets, prioritise 8h sleep"
        if recovery and recovery.has_data:
            if "declining" in recovery.trend_direction.lower() or "decreasing" in recovery.trend_direction.lower():
                this_week_action = "Reduce volume by 10-20%, prioritise recovery"
            else:
                this_week_action = "Maintain current volume, focus on sleep quality"

        review_note = "Review progress after this week\u2019s training"
        if plateau and plateau.has_data:
            try:
                plat_prob = float(plateau.probability.replace("%", ""))
            except (ValueError, AttributeError):
                plat_prob = 0
            if plat_prob > 0.5:
                review_note = "Monitor for plateau signs \u2014 reassess progression scheme"

        # Build action rows
        actions = [
            ("Today", today_action),
            ("This Week", this_week_action),
            ("Review", review_note),
        ]

        for day_label, action_text in actions:
            row = QFrame()
            row.setStyleSheet("background: transparent; border: none;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(0, _px4, 0, _px4)
            rl.setSpacing(_px12)

            day_badge = StatusBadge(text=day_label, level=StatusLevel.INFO, outlined=True)
            rl.addWidget(day_badge)

            action_lbl = QLabel(action_text)
            action_lbl.setStyleSheet(
                f"color: {colors.text_primary}; {font_style('body')}; background: transparent;"
            )
            action_lbl.setWordWrap(True)
            rl.addWidget(action_lbl, 1)

            self._action_card.add_content(row)

        # CTA buttons
        cta_row = QHBoxLayout()
        cta_row.setContentsMargins(0, _px12, 0, 0)
        cta_row.setSpacing(_px12)

        continue_btn = QPushButton("  \u25B6  Continue")
        continue_btn.setCursor(Qt.PointingHandCursor)
        continue_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(124,58,237,0.95), stop:0.5 rgba(147,51,234,0.9), stop:1 rgba(192,38,211,0.85));
                color: white;
                border-radius: {R.size_2xl};
                padding: 8px {S.s6};
                {font_style('body', 'bold')}
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(139,92,246,0.95), stop:0.5 rgba(167,139,250,0.9), stop:1 rgba(192,132,252,0.85));
            }}
        """)
        cta_row.addWidget(continue_btn)

        review_btn = QPushButton("  \u270F  Review Plan")
        review_btn.setCursor(Qt.PointingHandCursor)
        review_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {colors.text_primary};
                border: 1px solid {resolve_alpha(colors.primary, 0.12)};
                border-radius: {R.size_2xl};
                padding: 8px {S.s6};
                {font_style('body', 'bold')}
            }}
            QPushButton:hover {{
                background-color: {resolve_alpha(colors.primary, 0.10)};
                border-color: {resolve_alpha(colors.primary, 0.25)};
            }}
        """)
        cta_row.addWidget(review_btn)

        cta_row.addStretch()
        cta_container = QWidget()
        cta_container.setLayout(cta_row)
        self._action_card.add_content(cta_container)

    # ── Layout Helpers ───────────────────────────────────────────

    @staticmethod
    def _clear_layout(layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    @staticmethod
    def _clear_card_body(card: AppCard) -> None:
        body = getattr(card, "_body", None)
        if body is None:
            return
        while body.count():
            item = body.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
