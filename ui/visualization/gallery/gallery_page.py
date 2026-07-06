from __future__ import annotations

from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.design_system.components import SectionHeader
from ui.design_system.layout import ScrollContainer
from ui.design_system.tokens.color import ColorScheme, color_from_scheme
from ui.visualization.charts import AreaChart, BarChart, DeltaChart, TrendChart
from ui.visualization.curves import BodyweightCurve, PRCurve, RecoveryCurve, TrainingLoadCurve
from ui.visualization.graphs import EvidenceGraphView, KnowledgeGraphView, ReasonTreeView
from ui.visualization.heatmaps import (
    ComplianceHeatmap,
    FatigueHeatmap,
    MuscleHeatmap,
    VolumeHeatmap,
)
from ui.visualization.indicators import ConfidenceGauge, MomentumGauge, RiskGauge, StabilityGauge
from ui.visualization.rings import (
    ConfidenceRing,
    GoalRing,
    ProgressRingV2,
    ReadinessRing,
    RecoveryRing,
)
from ui.visualization.timelines import (
    AdaptationTimeline,
    PredictionTimeline,
    RecoveryTimeline,
    WeeklyTimeline,
)


class _Section(QGroupBox):
    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setTitle("")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(16, 12, 16, 16)
        self._layout.setSpacing(8)
        self._title = QLabel(title)
        self._title.setStyleSheet("font-size: 14px; font-weight: 700; color: #F1F5F9; background: transparent; border: none; padding: 0;")
        self._layout.addWidget(self._title)

    def add_row(self, *widgets: QWidget) -> None:
        row = QHBoxLayout()
        row.setSpacing(16)
        for w in widgets:
            row.addWidget(w)
        row.addStretch()
        self._layout.addLayout(row)

    def style(self, bg: str, border: str) -> None:
        self.setStyleSheet(f"QGroupBox {{ background: {bg}; border: 1px solid {border}; border-radius: 8px; }}")


class VisualizationGalleryPage(QWidget):
    """Gallery page showcasing every visualization component with sample data."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        colors = color_from_scheme(ColorScheme.DARK)
        scroll = ScrollContainer()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

        cl = scroll._wrapper.layout()
        cl.setContentsMargins(32, 24, 32, 32)
        cl.setSpacing(24)

        cl.addWidget(SectionHeader(title="Visualization Gallery", subtitle="All 34 visualization components with sample data"))

        rings = _Section("Rings")
        rings.style(colors.surface, colors.border)

        pr = ProgressRingV2(size=100, stroke_width=8)
        gr = GoalRing(size=100, stroke_width=8)
        rr = RecoveryRing(size=100, stroke_width=8)
        cr = ConfidenceRing(size=86, stroke_width=6)
        rdr = ReadinessRing(size=110, stroke_width=8)
        rings.add_row(pr, gr, rr, cr, rdr)

        pr.set_value(75, label="test")
        gr.set_goal(42, 100, label="test")
        rr.set_value(68, label="test")
        cr.set_confidence(0.85, label="test")
        rdr.set_readiness(58, label="test")
        cl.addWidget(rings)

        indicators_section = _Section("Indicators")
        indicators_section.style(colors.surface, colors.border)
        indicators_section.add_row(
            ConfidenceGauge(width=140, height=24),
            RiskGauge(width=140, height=24),
            StabilityGauge(width=140, height=24),
            MomentumGauge(width=140, height=24),
        )
        cg = indicators_section._layout.itemAt(1).layout().itemAt(0).widget()
        cg.set_confidence(0.82, "Confidence")
        rg = indicators_section._layout.itemAt(1).layout().itemAt(1).widget()
        rg.set_risk(0.35, "Risk")
        sg = indicators_section._layout.itemAt(1).layout().itemAt(2).widget()
        sg.set_stability(0.91, "Stability")
        mg = indicators_section._layout.itemAt(1).layout().itemAt(3).widget()
        mg.set_momentum(0.45, "Momentum")
        cl.addWidget(indicators_section)

        timelines_section = _Section("Timelines")
        timelines_section.style(colors.surface, colors.border)
        timelines_section.add_row(
            WeeklyTimeline(),
            PredictionTimeline(),
            RecoveryTimeline(),
            AdaptationTimeline(),
        )
        wt = timelines_section._layout.itemAt(1).layout().itemAt(0).widget()
        wt.set_data([30, 55, 45, 80, 60, 75, 90])
        pt = timelines_section._layout.itemAt(1).layout().itemAt(1).widget()
        pt.set_data([("W1", 0, 65), ("W2", 0, 70), ("W3", 0, 82), ("W4", 0, 78)], goal_line=80)
        rt = timelines_section._layout.itemAt(1).layout().itemAt(2).widget()
        rt.set_data([("M", 45), ("T", 60), ("W", 75), ("T", 55), ("F", 80)])
        at = timelines_section._layout.itemAt(1).layout().itemAt(3).widget()
        at.set_data([("W1", "completed", "Jan"), ("W2", "active", "Feb"), ("W3", "pending", "Mar")])
        cl.addWidget(timelines_section)

        heatmaps_section = _Section("Heatmaps")
        heatmaps_section.style(colors.surface, colors.border)
        heatmaps_section.add_row(
            MuscleHeatmap(),
            VolumeHeatmap(),
            FatigueHeatmap(),
            ComplianceHeatmap(),
        )
        mh = heatmaps_section._layout.itemAt(1).layout().itemAt(0).widget()
        mh.set_data([("Chest", 85), ("Back", 70), ("Legs", 90), ("Arms", 45)], max_volume=100)
        vh = heatmaps_section._layout.itemAt(1).layout().itemAt(1).widget()
        vh.set_data([("Mon", 3000), ("Tue", 4500), ("Wed", 2000), ("Thu", 5000), ("Fri", 3500)], max_val=5000)
        fh = heatmaps_section._layout.itemAt(1).layout().itemAt(2).widget()
        fh.set_data([("Upper", 30), ("Lower", 65), ("Core", 20), ("CNS", 80)], max_fatigue=100)
        ch = heatmaps_section._layout.itemAt(1).layout().itemAt(3).widget()
        ch.set_data([("Mon", 0.95), ("Tue", 0.85), ("Wed", 0.70), ("Thu", 0.90), ("Fri", 0.80)])
        cl.addWidget(heatmaps_section)

        charts_section = _Section("Charts")
        charts_section.style(colors.surface, colors.border)
        charts_section.add_row(
            TrendChart(),
            AreaChart(),
            DeltaChart(),
            BarChart(orientation="horizontal"),
        )
        tc = charts_section._layout.itemAt(1).layout().itemAt(0).widget()
        tc.set_data([("W1", 50), ("W2", 65), ("W3", 58), ("W4", 72), ("W5", 68)])
        ac = charts_section._layout.itemAt(1).layout().itemAt(1).widget()
        ac.set_data([("W1", 100), ("W2", 180), ("W3", 280), ("W4", 340), ("W5", 390)])
        dc = charts_section._layout.itemAt(1).layout().itemAt(2).widget()
        dc.set_data([("W2", 15), ("W3", -7), ("W4", 14), ("W5", -4)])
        bc = charts_section._layout.itemAt(1).layout().itemAt(3).widget()
        bc.set_data([("Bench", 185), ("Squat", 225), ("Deadlift", 315)], max_val=350)
        cl.addWidget(charts_section)

        graphs_section = _Section("Graphs")
        graphs_section.style(colors.surface, colors.border)
        graphs_section.add_row(
            KnowledgeGraphView(),
            EvidenceGraphView(),
            ReasonTreeView(),
        )
        kg = graphs_section._layout.itemAt(1).layout().itemAt(0).widget()
        kg.set_data(nodes=[("Strength", 1.0), ("Hyper", 0.8), ("Power", 0.6), ("Meta", 0.7), ("Recovery", 0.5)], edges=[(0, 1, "contains"), (0, 2, "contains"), (2, 3, "relates")])
        eg = graphs_section._layout.itemAt(1).layout().itemAt(1).widget()
        eg.set_data(nodes=[("E1", 0.9), ("E2", 0.7), ("E3", 0.8), ("E4", 0.6)], edges=[(0, 2, 0.8), (1, 2, 0.6), (2, 3, 0.7)])
        rt = graphs_section._layout.itemAt(1).layout().itemAt(2).widget()
        rt.set_data([("Goal", "conclusion"), ("Sub1", "premise"), ("Sub2", "premise"), ("Leaf", "premise")], root=0, children={0: [1, 2], 2: [3]})
        cl.addWidget(graphs_section)

        curves_section = _Section("Scientific Curves")
        curves_section.style(colors.surface, colors.border)
        curves_section.add_row(
            TrainingLoadCurve(),
            RecoveryCurve(),
            BodyweightCurve(),
            PRCurve(),
        )
        tl = curves_section._layout.itemAt(1).layout().itemAt(0).widget()
        tl.set_data([("W1", 60), ("W2", 75), ("W3", 85), ("W4", 95), ("W5", 70)], overload_threshold=80)
        rc = curves_section._layout.itemAt(1).layout().itemAt(1).widget()
        rc.set_data([("M", 45), ("T", 55), ("W", 70), ("T", 60), ("F", 80), ("S", 75)])
        bw = curves_section._layout.itemAt(1).layout().itemAt(2).widget()
        bw.set_data([("W1", 82), ("W2", 81.5), ("W3", 81), ("W4", 80.5), ("W5", 80)], goal_low=79, goal_high=81)
        pr = curves_section._layout.itemAt(1).layout().itemAt(3).widget()
        pr.set_data([("W1", 100, False), ("W2", 105, True), ("W3", 107, False), ("W4", 112, True), ("W5", 115, False)])
        cl.addWidget(curves_section)

        cl.addStretch()

        self.setStyleSheet(f"background-color: {colors.background};")
