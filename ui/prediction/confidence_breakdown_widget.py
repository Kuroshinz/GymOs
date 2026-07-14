from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from modules.prediction.domain import ExplainabilityDetail, PredictionResult
from modules.prediction.presentation import PredictionFormatter
from ui.dashboard.dashboard_widgets.base_card import DashboardCard


class ConfidenceBreakdownWidget(DashboardCard):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(title="CONFIDENCE BREAKDOWN", badge="Details", parent=parent)
        self._container = QVBoxLayout()
        self._container.setContentsMargins(0, 0, 0, 0)
        self._container.setSpacing(6)
        self.add_layout(self._container)
        self._empty = QLabel("No confidence breakdown data available")
        self._empty.setStyleSheet("color: #64748B; font-size: 13px;")
        self._container.addWidget(self._empty)

    def update_data(self, result: PredictionResult | None) -> None:
        while self._container.count():
            item = self._container.takeAt(0)
            if item and item.widget():
                item.widget().deleteLater()

        if not result or not result.explainability:
            self._container.addWidget(self._empty)
            return

        has_breakdown = False
        for key, detail in result.explainability.items():
            mr = detail.mr_explanation
            if mr and (mr.confidence_breakdown or mr.evidence_summary or mr.assumptions_used or mr.risk_flags):
                has_breakdown = True
                section = self._build_breakdown_section(key, detail)
                self._container.addWidget(section)

        if not has_breakdown:
            self._container.addWidget(self._empty)

    def _build_breakdown_section(self, key: str, detail: ExplainabilityDetail) -> QWidget:
        section = QWidget()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        mr = detail.mr_explanation

        header = QLabel(f"[{key}]")
        header.setStyleSheet("color: #818CF8; font-size: 11px; font-weight: 600; padding: 2px 0;")
        layout.addWidget(header)

        if mr.confidence_breakdown:
            for factor, score in mr.confidence_breakdown.items():
                try:
                    score_f = float(score)
                    score_str = f"{score_f:.0%}"
                    level = "high" if score_f >= 0.7 else "moderate" if score_f >= 0.4 else "low"
                except ValueError:
                    score_str = str(score)
                    level = score.lower() if isinstance(score, str) else "moderate"
                color = PredictionFormatter.impact_level_color(level)
                row = DashboardCard.make_row(factor, score_str, value_color=color)
                layout.addWidget(row)

        if mr.evidence_summary:
            layout.addWidget(DashboardCard.make_separator())
            ev_header = QLabel("Evidence")
            ev_header.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 600; padding: 2px 0;")
            layout.addWidget(ev_header)
            for ev in mr.evidence_summary[:5]:
                source = ev.get("source", "")
                rel = ev.get("relevance", 0)
                ev_row = DashboardCard.make_row(
                    source[:40],
                    f"rel: {rel:.0%}",
                    value_color=PredictionFormatter.impact_level_color("high" if rel >= 0.7 else "moderate"),
                )
                layout.addWidget(ev_row)

        if mr.assumptions_used:
            layout.addWidget(DashboardCard.make_separator())
            as_header = QLabel("Assumptions")
            as_header.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 600; padding: 2px 0;")
            layout.addWidget(as_header)
            for assumption in mr.assumptions_used:
                a = QLabel(f"• {assumption}")
                a.setStyleSheet("color: #64748B; font-size: 12px; padding-left: 8px;")
                a.setWordWrap(True)
                layout.addWidget(a)

        if mr.risk_flags:
            layout.addWidget(DashboardCard.make_separator())
            rf_header = QLabel("Risk Flags")
            rf_header.setStyleSheet("color: #EF4444; font-size: 11px; font-weight: 600; padding: 2px 0;")
            layout.addWidget(rf_header)
            for flag in mr.risk_flags:
                f = QLabel(f"⚠ {flag}")
                f.setStyleSheet("color: #FB923C; font-size: 12px; padding-left: 8px;")
                f.setWordWrap(True)
                layout.addWidget(f)

        return section
