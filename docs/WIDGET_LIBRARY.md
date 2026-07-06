# GymOS Command Center — Widget Library

## Visualization Components

| Component | File | Description |
|-----------|------|-------------|
| `ConfidenceIndicator` | `confidence_indicator.py` | Circular confidence gauge (60x60) |
| `ConfidenceBar` | `confidence_indicator.py` | Horizontal confidence bar with label |
| `TrendChart` | `trend_chart.py` | Line chart with trend indicator |
| `PredictionCard` | `prediction_card.py` | Prediction display card (240x130) |
| `TimelineWidget` | `timeline.py` | Vertical timeline with date/subtitle |
| `RelationshipGraph` | `relationship_graph.py` | Force-like node-edge graph |
| `ProgressRing` | `progress_ring.py` | Circular progress indicator |
| `HeatmapWidget` | `heatmap.py` | Value grid with color intensity |

## Layout Components

| Component | File | Description |
|-----------|------|-------------|
| `GridPanel` | `grid_panel.py` | Responsive grid layout |
| `DockablePanel` | `dockable_panel.py` | Panel with dock/close controls |
| `ResizableWidget` | `resizable_widget.py` | Widget with resize handles |

## Navigation Components

| Component | File | Description |
|-----------|------|-------------|
| `Sidebar` | `sidebar.py` | Left navigation panel (220px) |
| `SidebarButton` | `sidebar.py` | Active-state nav button |
| `Breadcrumb` | `breadcrumb.py` | Path indicator with clickable segments |
| `QuickSearch` | `quick_search.py` | Search input with dropdown results |
| `CommandPalette` | `command_palette.py` | Ctrl+K modal command palette |

## Data Models (16 dataclasses)

All in `models.py`:
- `CommandCenterData` — aggregate payload for all pages
- `MissionData`, `IntentData` — mission page
- `AdaptiveTimelineItem`, `DecisionTimelineItem` — timeline entries
- `KnowledgeUpdateItem` — knowledge feed entry
- `PredictionSummaryData` — prediction cards
- `OptimizationInsightData` — optimization insights
- `RecoveryOverviewData`, `TrainingReadinessData` — recovery
- `CurrentMesocycleData`, `WeeklyReviewData` — planning
- `SystemHealthData`, `CapabilityProgressData` — health/capabilities
- `ReleaseReadinessData`, `KernelRuntimeData`, `ProductStateData` — system
- `KnowledgeGraphData` — knowledge graph

## Widget Usage Example

```python
from ui.command_center.widgets.intent_card_widget import IntentCardWidget
from ui.command_center.models import IntentData

widget = IntentCardWidget()
data = IntentData(
    current_goal="Build Muscle",
    progress_percent=65.0,
    weekly_rate=0.35,
    adherence=0.85,
    phase="Hypertrophy",
)
widget.set_data(data)
```
