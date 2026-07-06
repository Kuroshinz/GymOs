# GymOS Experience Platform Architecture

## Overview

The Experience Platform is a cross-cutting UI infrastructure layer that provides all interaction, workflow, layout, and usability features for GymOS. It transforms the application from a functional tool into a polished, premium desktop experience.

## Design Principles

1. **No business logic** — engines are pure UX infrastructure, zero domain knowledge
2. **Theme-only visuals** — all colors/tokens from `ui.command_center.theme.C`, no hardcoded values
3. **Event-driven** — Qt Signals for loose coupling between engines
4. **Deterministic** — no randomness, fixed-duration animations
5. **Keyboard-first** — all features accessible via shortcuts or command palette
6. **Persistent** — layouts, window states, and preferences persist across sessions

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                 ExperienceManager                    │
│  (Orchestrator — owns all engines)                  │
├─────────────────────────────────────────────────────┤
│  Animation │ Layout │ Navigation │ Interaction      │
│  Shortcuts  │ CommandPalette │ Search               │
│  Notifications │ Loading │ EmptyStates │ Focus      │
│  WindowLayout │ Workspaces │ Workflows │ Theme      │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│            ui/command_center/ Pages                 │
│  (Consumes ExperienceManager engines)               │
└─────────────────────────────────────────────────────┘
```

## Engine Catalog

| Engine | File | Purpose | Key Signals |
|--------|------|---------|-------------|
| AnimationManager | `animation_manager.py` | Fade, slide, scale, bounce, pulse | `animation_started`, `animation_completed` |
| LayoutEngine | `layout_engine.py` | Responsive grid, panel containers, layout persistence | `layout_saved`, `layout_loaded` |
| NavigationEngine | `navigation_engine.py` | Route registry, history, breadcrumbs | `navigated`, `back_available`, `forward_available` |
| InteractionEngine | `interaction_engine.py` | Hover effects, tooltips, drag-drop | `hover_entered`, `hover_exited` |
| ShortcutManager | `shortcut_manager.py` | Keyboard shortcut registration with context scoping | `shortcut_triggered` |
| CommandPaletteEngine | `command_palette_engine.py` | Command registry, search, modal dialog | `command_registered`, `command_executed` |
| SearchProvider | `search_provider.py` | Pluggable global search with relevance scoring | `search_started`, `search_completed` |
| NotificationCenter | `notification_center.py` | Toast notifications, history, prioritization | `notification_received`, `notification_dismissed` |
| LoadingStateManager | `loading_state_manager.py` | Skeleton screens, overlays, progress bars | — |
| EmptyStateManager | `empty_state_manager.py` | Configurable empty states with CTAs | `shown`, `hidden` |
| FocusMode | `focus_mode.py` | Distraction-free mode | `focus_entered`, `focus_exited` |
| WindowLayoutManager | `window_layout_manager.py` | Window geometry persistence | `state_saved`, `state_restored` |
| WorkspaceManager | `workspace_manager.py` | Multi-workspace management | `workspace_created`, `workspace_switched` |
| WorkflowEngine | `workflow_engine.py` | Multi-step guided workflows | `workflow_started`, `workflow_completed` |
| ThemeTransitionManager | `theme_transition_manager.py` | Animated theme transitions | `transition_started`, `transition_completed` |

## Data Flow

```
User Input (keyboard/mouse)
    │
    ├──→ ShortcutManager → callback/command
    ├──→ CommandPaletteEngine → execute command
    ├──→ NavigationEngine → navigate route
    ├──→ InteractionEngine → hover/tooltip
    │
    ▼
ExperienceManager.propagate_data(data)
    │
    ▼
Pages.update_data(data)
    │
    ▼
Widgets.set_data(model)
```

## Integration Points

| Integration | Method |
|-------------|--------|
| Command Center pages | `navigation.register_route(Route(...))` |
| Command palette | `command_palette.register(CommandItem(...))` |
| Shortcuts | `shortcuts.register(Shortcut(...))` |
| Search | `search.register_provider(name, fn)` |
| Sidebar/top bar | `focus.register_sidebar(widget)` / `focus.register_top_bar(widget)` |
| Window state | `window_layout.save_persistent()` / `window_layout.load_persistent()` |
| Layout | `layout.register_grid(id, grid)` / `layout.save_layout(name)` |
