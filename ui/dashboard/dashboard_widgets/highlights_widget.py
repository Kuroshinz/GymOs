"""Bottom highlights row — Achievements, Streak, Next Milestone, Body Weight."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from ui.dashboard.dashboard_models import DashboardData
from ui.dashboard.dashboard_widgets.card_kit import PanelCard, make_label, qcolor
from ui.design_system.tokens.color import ColorScheme, color_from_scheme, resolve_alpha

C = color_from_scheme(ColorScheme.DARK)

_TIER_COLORS = {
    "bronze": "#CD7F32",
    "silver": "#C0C7D1",
    "gold": "#F5B940",
    "platinum": "#7DE2FC",
}


class Sparkline(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._series: list[float] = []
        self.setMinimumHeight(56)
        self.setStyleSheet("background: transparent;")

    def set_series(self, series: list[float]) -> None:
        self._series = list(series)
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        n = len(self._series)
        if n < 2:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        h = self.height()
        lo = min(self._series)
        hi = max(self._series)
        rng = (hi - lo) or 1.0

        def xp(i): return w * i / (n - 1)
        def yp(v): return h - 6 - (v - lo) / rng * (h - 12)

        path = QPainterPath()
        path.moveTo(QPointF(xp(0), yp(self._series[0])))
        for i in range(1, n):
            path.lineTo(QPointF(xp(i), yp(self._series[i])))

        fill = QPainterPath(path)
        fill.lineTo(xp(n - 1), h)
        fill.lineTo(xp(0), h)
        fill.closeSubpath()
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, qcolor(C.primary, 0.35))
        grad.setColorAt(1.0, qcolor(C.primary, 0.0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(grad)
        painter.drawPath(fill)

        painter.setPen(QPen(QColor(C.secondary), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)
        painter.end()


class HighlightsWidget(QWidget):
    def __init__(self, motion: Any = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._motion = motion
        self.setStyleSheet("background: transparent;")

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(16)

        row.addWidget(self._build_achievements(), 3)
        row.addWidget(self._build_streak(), 2)
        row.addWidget(self._build_milestone(), 3)
        row.addWidget(self._build_bodyweight(), 3)

    def set_motion_service(self, motion: Any) -> None:
        self._motion = motion

    # ── Achievements ──────────────────────────────────────────
    def _build_achievements(self) -> PanelCard:
        card = PanelCard(title="Achievements")
        self._badges_row = QHBoxLayout()
        self._badges_row.setContentsMargins(0, 0, 0, 0)
        self._badges_row.setSpacing(8)
        self._badges_row.addStretch()
        card.add_layout(self._badges_row)
        self._badge_labels: list[QLabel] = []
        return card

    # ── Streak ────────────────────────────────────────────────
    def _build_streak(self) -> PanelCard:
        card = PanelCard(title="Streak")
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)
        col = QVBoxLayout()
        col.setSpacing(0)
        self._streak_value = make_label("0", size=34, weight=800, color=C.text_primary)
        col.addWidget(self._streak_value)
        col.addWidget(make_label("Days", size=12, weight=500, color=C.text_secondary))
        row.addLayout(col)
        row.addStretch()
        flame = QLabel("\U0001F525")
        flame.setStyleSheet("font-size: 34px; background: transparent;")
        row.addWidget(flame, 0, Qt.AlignVCenter)
        card.add_layout(row)
        card.add_stretch()
        return card

    # ── Next Milestone ────────────────────────────────────────
    def _build_milestone(self) -> PanelCard:
        card = PanelCard(title="Next Milestone")
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        self._milestone_label = make_label("--", size=16, weight=700, color=C.text_primary)
        top.addWidget(self._milestone_label)
        top.addStretch()
        gem = QLabel("\U0001F48E")
        gem.setStyleSheet("font-size: 22px; background: transparent;")
        top.addWidget(gem)
        card.add_layout(top)

        self._milestone_bar = QProgressBar()
        self._milestone_bar.setTextVisible(False)
        self._milestone_bar.setFixedHeight(10)
        self._milestone_bar.setRange(0, 100)
        self._milestone_bar.setStyleSheet(
            f"""
            QProgressBar {{ background: {resolve_alpha(C.primary, 0.15)}; border: none; border-radius: 5px; }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {C.primary}, stop:1 {C.secondary});
                border-radius: 5px;
            }}
            """
        )
        card.add_widget(self._milestone_bar)
        card.add_stretch()
        return card

    # ── Body Weight ───────────────────────────────────────────
    def _build_bodyweight(self) -> PanelCard:
        card = PanelCard(title="Body Weight")
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        col = QVBoxLayout()
        col.setSpacing(2)
        self._weight_value = make_label("-- kg", size=24, weight=800, color=C.text_primary)
        col.addWidget(self._weight_value)
        self._weight_delta = make_label("", size=12, weight=500, color=C.success)
        col.addWidget(self._weight_delta)
        top.addLayout(col)
        top.addStretch()
        card.add_layout(top)

        self._sparkline = Sparkline()
        card.add_widget(self._sparkline)
        return card

    # ── Data ──────────────────────────────────────────────────
    def update_data(self, data: DashboardData) -> None:
        # Achievements
        for lbl in self._badge_labels:
            lbl.setParent(None)
        self._badge_labels.clear()
        for ach in (data.achievements or [])[:7]:
            tier = ach.get("tier", "bronze")
            unlocked = ach.get("unlocked", False)
            color = _TIER_COLORS.get(tier, "#CD7F32")
            badge = QLabel("\U0001F3C5")
            badge.setFixedSize(36, 36)
            badge.setAlignment(Qt.AlignCenter)
            badge.setToolTip(ach.get("name", ""))
            if unlocked:
                badge.setStyleSheet(
                    f"background: {resolve_alpha(color, 0.20)}; border-radius: 12px; font-size: 18px;"
                )
            else:
                badge.setStyleSheet(
                    f"background: {resolve_alpha('#5B5F88', 0.12)}; border-radius: 12px; font-size: 18px;"
                )
                badge.setText("\U0001F512")
            self._badges_row.insertWidget(self._badges_row.count() - 1, badge)
            self._badge_labels.append(badge)

        # Streak
        self._streak_value.setText(str(data.current_streak))

        # Milestone
        self._milestone_label.setText(data.milestone_label or "--")
        pct = int(data.xp_current / data.xp_target * 100) if data.xp_target else 0
        self._milestone_bar.setValue(min(pct, 100))

        # Body weight
        series = data.body_weight_series or []
        if series:
            self._weight_value.setText(f"{series[-1]:.1f} kg")
        self._weight_delta.setText(data.body_weight_delta or "")
        delta_color = C.success if not (data.body_weight_delta or "").startswith("-") else C.error
        self._weight_delta.setStyleSheet(
            f"color: {delta_color}; font-size: 12px; font-weight: 500; background: transparent;"
        )
        self._sparkline.set_series(series)
