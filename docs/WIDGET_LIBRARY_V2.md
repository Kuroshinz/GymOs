# GymOS Experience Platform — Widget & Engine Catalog

## Layout Components

| Component | File | Description |
|-----------|------|-------------|
| `ResponsiveGrid` | `layout_engine.py` | Responsive grid with breakpoints (xs=1, sm=2, md=3, lg=4, xl=6 cols) |
| `PanelContainer` | `layout_engine.py` | Framed panel with title, minimize toggle, close signal |
| `PanelState` | `layout_engine.py` | Dataclass for panel position, visibility, span |
| `LayoutConfig` | `layout_engine.py` | Columns, spacing, margins, breakpoints configuration |
| `LayoutEngine` | `layout_engine.py` | Grid registration, layout save/load/serialize/deserialize |

## Navigation Components

| Component | File | Description |
|-----------|------|-------------|
| `NavigationEngine` | `navigation_engine.py` | Route registration, back/forward history, breadcrumbs |
| `Route` | `navigation_engine.py` | Route dataclass with id, widget, parent, title, category |
| `BreadcrumbEntry` | `navigation_engine.py` | Breadcrumb trail entry |

## Animation Components

| Component | File | Description |
|-----------|------|-------------|
| `AnimationManager` | `animation_manager.py` | Fade, slide, scale, bounce, pulse animations |
| `AnimationHandle` | `animation_manager.py` | Handle for animation lifecycle (stop, pause, resume) |
| `AnimationPreset` | `animation_manager.py` | Duration/easing presets (fast=150ms, normal=300ms, slow=500ms) |

## Interaction Components

| Component | File | Description |
|-----------|------|-------------|
| `InteractionEngine` | `interaction_engine.py` | Hover, tooltip, drag-drop management |
| `HoverWatcher` | `interaction_engine.py` | Event-filter based hover detection |
| `TooltipManager` | `interaction_engine.py` | Tooltip registration with delay |
| `HoverEffect` | `interaction_engine.py` | Style/cursor/opacity on hover |
| `DragDropConfig` | `interaction_engine.py` | Drag/drop capability flags |

## Shortcut Components

| Component | File | Description |
|-----------|------|-------------|
| `ShortcutManager` | `shortcut_manager.py` | Centralized shortcut registry with context scoping |
| `Shortcut` | `shortcut_manager.py` | Shortcut dataclass: id, key_sequence, callback, context |

## Command Palette Components

| Component | File | Description |
|-----------|------|-------------|
| `CommandPaletteEngine` | `command_palette_engine.py` | Command registry, search, category grouping |
| `CommandPaletteDialog` | `command_palette_engine.py` | Modal search dialog with filtered list |
| `CommandItem` | `command_palette_engine.py` | Command dataclass: id, label, description, category, shortcut |

## Search Components

| Component | File | Description |
|-----------|------|-------------|
| `SearchProvider` | `search_provider.py` | Pluggable search with relevance scoring |
| `SearchResult` | `search_provider.py` | Result dataclass: id, title, description, category, relevance |

## Notification Components

| Component | File | Description |
|-----------|------|-------------|
| `NotificationCenter` | `notification_center.py` | Toast notifications + history |
| `NotificationToast` | `notification_center.py` | Floating toast with auto-dismiss |
| `NotificationList` | `notification_center.py` | Scrollable notification history panel |
| `NotificationItem` | `notification_center.py` | Notification dataclass with priority, timestamp |

## Loading State Components

| Component | File | Description |
|-----------|------|-------------|
| `LoadingStateManager` | `loading_state_manager.py` | Show/hide overlays and skeletons |
| `SkeletonWidget` | `loading_state_manager.py` | Pulsing placeholder bar |
| `SkeletonBlock` | `loading_state_manager.py` | Card-sized skeleton block with multiple lines |
| `LoadingOverlay` | `loading_state_manager.py` | Spinning indicator overlay |
| `ProgressIndicator` | `loading_state_manager.py` | Determinate/indeterminate progress bar |

## Empty State Components

| Component | File | Description |
|-----------|------|-------------|
| `EmptyStateManager` | `empty_state_manager.py` | Show/hide empty state widgets |
| `EmptyStateWidget` | `empty_state_manager.py` | Icon + title + description + CTA button |
| `EmptyStateConfig` | `empty_state_manager.py` | Configuration dataclass |

## Focus Mode

| Component | File | Description |
|-----------|------|-------------|
| `FocusMode` | `focus_mode.py` | Distraction-free mode hiding chrome elements |

## Workspace Components

| Component | File | Description |
|-----------|------|-------------|
| `WorkspaceManager` | `workspace_manager.py` | Multi-workspace create/switch/close/rename |
| `Workspace` | `workspace_manager.py` | Workspace dataclass: id, name, widget, layout_state |

## Workflow Components

| Component | File | Description |
|-----------|------|-------------|
| `WorkflowEngine` | `workflow_engine.py` | Multi-step workflow registration and execution |
| `Workflow` | `workflow_engine.py` | Workflow dataclass: steps, callbacks |
| `Step` | `workflow_engine.py` | Step dataclass: title, description, validator |
| `WorkflowDialog` | `workflow_engine.py` | Modal step-by-step dialog |
