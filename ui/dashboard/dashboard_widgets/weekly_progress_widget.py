"""Weekly Progress card — dual line chart (Strength / Cardio) + stat row."""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from ui.dashboard.dashboard_models import DashboardData
from ui.dashboard.dashboard_widgets.card_kit import PanelCard, make_label, qcolor
from ui.design_system.tokens.color import ColorScheme, color_from_scheme, resolve_alpha

C = color_from_scheme(ColorScheme.DARK)

_STRENGTH = "#A855F7"
_CARDIO = "#38BDF8"


class DualLineChart(QWidget):
    """Two smooth gradient-filled line series over weekday labels."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._labels: list[str] = []
        self._strength: list[float] = []
        self._cardio: list[float] = []
        self.setMinimumHeight(240)
        self.setStyleSheet("background: transparent;")

    def set_data(self, labels: list[str], strength: list[float], cardio: list[float]) -> None:
        self._labels = list(labels)
        self._strength = list(strength)
        self._cardio = list(cardio)
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()
        left_pad = 42
        right_pad = 12
        top_pad = 12
        bottom_pad = 28
        plot_w = w - left_pad - right_pad
        plot_h = h - top_pad - bottom_pad

        # Gridlines + y-axis labels (0/25/50/75/100%).
        grid_pen = QPen(qcolor(C.text_secondary, 0.10), 1)
        painter.setFont(_font(10))
        for i in range(5):
            frac = i / 4
            y = top_pad + plot_h * frac
            painter.setPen(grid_pen)
            painter.drawLine(int(left_pad), int(y), int(w - right_pad), int(y))
            painter.setPen(QColor(C.text_disabled))
            painter.drawText(
                QRectF(0, y - 8, left_pad - 8, 16),
                Qt.AlignRight | Qt.AlignVCenter,
                f"{100 - i * 25}%",
            )

        n = len(self._strength)
        if n < 2:
            painter.end()
            return

        def xp(i: int) -> float:
            return left_pad + plot_w * i / (n - 1)

        def yp(v: float) -> float:
            return top_pad + plot_h * (1 - max(0.0, min(v, 100.0)) / 100.0)

        # X labels.
        painter.setPen(QColor(C.text_disabled))
        painter.setFont(_font(10))
        for i, label in enumerate(self._labels[:n]):
            painter.drawText(
                QRectF(xp(i) - 20, h - bottom_pad + 4, 40, 16),
                Qt.AlignCenter,
                label,
            )

        self._draw_series(painter, self._cardio, _CARDIO, xp, yp, plot_h, top_pad)
        self._draw_series(painter, self._strength, _STRENGTH, xp, yp, plot_h, top_pad)
        painter.end()

    def _draw_series(self, painter, series, color, xp, yp, plot_h, top_pad) -> None:
        n = len(series)
        if n < 2:
            return
        pts = [QPointF(xp(i), yp(series[i])) for i in range(n)]

        # Smooth path (Catmull-Rom -> cubic).
        path = QPainterPath()
        path.moveTo(pts[0])
        for i in range(n - 1):
            p0 = pts[i - 1] if i > 0 else pts[i]
            p1 = pts[i]
            p2 = pts[i + 1]
            p3 = pts[i + 2] if i + 2 < n else pts[i + 1]
            c1 = QPointF(p1.x() + (p2.x() - p0.x()) / 6.0, p1.y() + (p2.y() - p0.y()) / 6.0)
            c2 = QPointF(p2.x() - (p3.x() - p1.x()) / 6.0, p2.y() - (p3.y() - p1.y()) / 6.0)
            path.cubicTo(c1, c2, p2)

        # Fill under curve.
        fill = QPainterPath(path)
        base_y = top_pad + plot_h
        fill.lineTo(pts[-1].x(), base_y)
        fill.lineTo(pts[0].x(), base_y)
        fill.closeSubpath()
        grad = QLinearGradient(0, top_pad, 0, base_y)
        grad.setColorAt(0.0, qcolor(color, 0.32))
        grad.setColorAt(1.0, qcolor(color, 0.0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(grad)
        painter.drawPath(fill)

        # Line.
        painter.setPen(QPen(QColor(color), 2.5))
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

        # Dots.
        painter.setBrush(QColor(C.background))
        painter.setPen(QPen(QColor(color), 2.5))
        for p in pts:
            painter.drawEllipse(p, 3.5, 3.5)


def _font(size: int, bold: bool = False) -> QFont:
    f = QFont("Inter")
    f.setPixelSize(size)
    f.setBold(bold)
    return f


class WeeklyProgressWidget(PanelCard):
    def __init__(self, motion: Any = None, parent: QWidget | None = None) -> None:
        super().__init__(title="Weekly Progress", parent=parent)
        self._motion = motion

        legend = QHBoxLayout()
        legend.setContentsMargins(0, 0, 0, 0)
        legend.setSpacing(18)
        legend.addLayout(_legend_item("Strength", _STRENGTH))
        legend.addLayout(_legend_item("Cardio", _CARDIO))
        legend.addStretch()
        self.add_layout(legend)

        self._chart = DualLineChart()
        self.add_widget(self._chart, 1)

        self._stats = QHBoxLayout()
        self._stats.setContentsMargins(0, 6, 0, 0)
        self._stats.setSpacing(12)
        self._stat_widgets: dict[str, tuple] = {}
        for key, caption in (
            ("workouts", "Workouts"),
            ("sets", "Sets Completed"),
            ("volume", "Volume"),
            ("prs", "PRs"),
        ):
            block, value_lbl, sub_lbl = _stat_block(caption)
            self._stat_widgets[key] = (value_lbl, sub_lbl)
            self._stats.addWidget(block, 1)
        self.add_layout(self._stats)

    def set_motion_service(self, motion: Any) -> None:
        self._motion = motion

    def update_data(self, data: DashboardData) -> None:
        self._chart.set_data(data.weekly_labels, data.weekly_strength, data.weekly_cardio)

        wv, ws = self._stat_widgets["workouts"]
        wv.setText(f"{data.week_workouts_done} / {data.week_workouts_target}")
        pct = int(data.week_workouts_done / data.week_workouts_target * 100) if data.week_workouts_target else 0
        ws.setText(f"{pct}%")

        sv, ss = self._stat_widgets["sets"]
        sv.setText(f"{data.week_sets_done} / {data.week_sets_target}")
        spct = int(data.week_sets_done / data.week_sets_target * 100) if data.week_sets_target else 0
        ss.setText(f"{spct}%")

        vv, vs = self._stat_widgets["volume"]
        vv.setText(f"{data.week_volume_kg:,.0f} kg")
        vs.setText(data.week_volume_delta)

        pv, ps = self._stat_widgets["prs"]
        pv.setText(f"{data.week_prs}")
        ps.setText("This week")


def _legend_item(text: str, color: str) -> QHBoxLayout:
    row = QHBoxLayout()
    row.setContentsMargins(0, 0, 0, 0)
    row.setSpacing(7)
    dot = make_label("\u25CF", size=11, color=color)
    row.addWidget(dot)
    row.addWidget(make_label(text, size=12, weight=500, color=C.text_secondary))
    return row


def _stat_block(caption: str):
    from PySide6.QtWidgets import QFrame

    block = QFrame()
    block.setStyleSheet(
        f"QFrame {{ background: {resolve_alpha(C.primary, 0.06)}; border-radius: 12px; }}"
    )
    lay = QVBoxLayout(block)
    lay.setContentsMargins(14, 12, 14, 12)
    lay.setSpacing(4)
    lay.addWidget(make_label(caption, size=11, weight=600, color=C.text_secondary, uppercase=True, letter_spacing="0.03em"))
    value = make_label("--", size=18, weight=800, color=C.text_primary)
    lay.addWidget(value)
    sub = make_label("", size=12, weight=600, color=C.success)
    lay.addWidget(sub)
    return block, value, sub
