# Visualization Platform — RFC-027.5

Single visualization SDK used by every GymOS page.

## Structure

```
ui/visualization/
├── __init__.py                    # Public API — re-exports everything
├── core/
│   ├── __init__.py
│   ├── base.py                    # BaseVisualization — theme, animation, interaction, accessibility, export
│   └── utils.py                   # clamp, lerp, interpolate_color, value_to_color
├── rings/
│   ├── __init__.py
│   ├── progress_ring_v2.py        # Circular progress — animated, token-colored
│   ├── goal_ring.py               # Goal progress ring
│   ├── recovery_ring.py           # Recovery score ring
│   ├── confidence_ring.py         # Confidence / certainty ring
│   └── readiness_ring.py          # Training readiness ring with sub-metric
├── timelines/
│   ├── __init__.py
│   ├── prediction_timeline.py     # Line chart with goal line
│   ├── recovery_timeline.py       # Area-style recovery history
│   ├── workout_timeline.py        # Volume bars per session
│   ├── weekly_timeline.py         # 7-day bar chart
│   ├── mesocycle_timeline.py      # Phase-colored segment bar
│   └── adaptation_timeline.py     # Event node timeline
├── heatmaps/
│   ├── __init__.py
│   ├── muscle_heatmap.py          # Muscle group volume bars
│   ├── volume_heatmap.py          # Volume distribution heatmap
│   ├── fatigue_heatmap.py         # Fatigue level heatmap (green→red)
│   └── compliance_heatmap.py      # Adherence rate heatmap
├── charts/
│   ├── __init__.py
│   ├── trend_chart.py             # Line chart for metric trends
│   ├── area_chart.py              # Filled area chart
│   ├── delta_chart.py             # Up/down delta bars
│   ├── comparison_chart.py        # Grouped bar comparison
│   ├── radar_chart.py             # Multi-dimensional spider chart
│   └── bar_chart.py               # Vertical or horizontal bars
├── graphs/
│   ├── __init__.py
│   ├── knowledge_graph_view.py    # Node-link domain knowledge graph
│   ├── evidence_graph_view.py     # Confidence-weighted directed graph
│   ├── reason_tree_view.py        # Tree reasoning chains
│   └── dependency_graph_view.py   # DAG module dependency view
├── indicators/
│   ├── __init__.py
│   ├── confidence_gauge.py        # Horizontal confidence bar
│   ├── risk_gauge.py              # Segmented risk meter
│   ├── stability_gauge.py         # Centered stability indicator
│   └── momentum_gauge.py          # Bidirectional trend gauge
├── curves/
│   ├── __init__.py
│   ├── training_load_curve.py     # Volume × intensity curve
│   ├── recovery_curve.py          # Recovery zone curve
│   ├── macro_curve.py             # Multi-series macronutrient curve
│   ├── bodyweight_curve.py        # Weight trend with goal band
│   └── pr_curve.py                # PR event-highlighted progression
└── gallery/
    ├── __init__.py
    └── gallery_page.py            # Gallery page showcasing all 34 components
```

## BaseVisualization

All components extend `BaseVisualization` (QFrame) which provides:

| Capability | Implementation |
|-----------|---------------|
| **Design tokens** | `_colors()` returns token object from `color_from_scheme()` |
| **Theme support** | `set_color_scheme(ColorScheme)` — updates all rendering |
| **Animation** | `animate(target, duration, easing)` — QVariantAnimation with token-driven defaults |
| **Reduced motion** | `set_reduced_motion(bool)` — skips animation, jumps to target |
| **Hover** | `enterEvent`/`leaveEvent` — sets `_hovered` flag, emits `hovered(text)` |
| **Click** | `mousePressEvent` — toggles `_selected`, emits `clicked()` |
| **Double-click** | Emits `double_clicked()` |
| **Zoom** | `wheelEvent` — adjusts `_zoom_level` (0.5x–3.0x), emits `zoom_changed(level)` |
| **Pan** | `_pan_offset` (QPointF) — available for subclasses |
| **Keyboard** | Escape deselects, Enter/Space toggles selection |
| **Tooltips** | `set_tooltip_text(text)` — displayed on hover |
| **Focus** | `StrongFocus` policy, visible focus indicators |
| **High contrast** | Via `ColorScheme.HIGH_CONTRAST` |
| **Export PNG** | `export_png(path)` — grabs widget and saves as PNG |
| **Export clipboard** | `export_to_clipboard()` — copies image to clipboard |
| **Accessible labels** | `set_accessible_label()` / `set_accessible_description()` |

### Signals

| Signal | Args | Trigger |
|--------|------|---------|
| `clicked` | () | Mouse press or Enter/Space key |
| `double_clicked` | () | Double-click |
| `hovered` | `str` | Mouse enter with tooltip text |
| `value_changed` | `float` | Animation value update |
| `zoom_changed` | `float` | Wheel scroll |

## Usage Pattern

```python
from ui.visualization import ConfidenceGauge

gauge = ConfidenceGauge(width=200, height=28)
gauge.set_confidence(0.85, "Prediction Confidence")
gauge.set_color_scheme(ColorScheme.LIGHT)
gauge.set_tooltip_text("85% confidence in this prediction")
gauge.animate_to(0.95)  # smooth transition
gauge.export_png("confidence.png")
```

## Backward Compatibility

Existing imports from `ui.design_system.visualization` continue to work — the
`__init__.py` now re-exports from `ui.visualization`. All legacy class names
are preserved; `RiskMeter` is aliased to `RiskGauge`.

## Gallery

`VisualizationGalleryPage` in `ui/visualization/gallery/` renders every
component with sample data, organized by category. Import and display it
like any other page:

```python
from ui.visualization.gallery import VisualizationGalleryPage
```

## Component Inventory

| Category | Count | Widgets |
|----------|-------|---------|
| Rings | 5 | ProgressRingV2, GoalRing, RecoveryRing, ConfidenceRing, ReadinessRing |
| Timelines | 6 | Prediction, Recovery, Workout, Weekly, Mesocycle, Adaptation |
| Heatmaps | 4 | Muscle, Volume, Fatigue, Compliance |
| Charts | 6 | Trend, Area, Delta, Comparison, Radar, Bar |
| Graphs | 4 | KnowledgeGraph, EvidenceGraph, ReasonTree, DependencyGraph |
| Indicators | 4 | Confidence, Risk, Stability, Momentum |
| Curves | 5 | TrainingLoad, Recovery, Macro, Bodyweight, PR |
| **Total** | **34** | |
