# ADR-018: GymOS Experience Platform

## Status

Accepted

## Context

GymOS has completed its core platform architecture (Planning, Optimizer, Knowledge, Evolution, Adaptive, Prediction, Recovery, Decision). The existing UI layer is functional but lacks the polish, responsiveness, and productivity features expected of a premium desktop application. Users interact with the Command Center through basic navigation without keyboard-first workflows, animations, persistent layouts, or modern UX patterns.

## Decision

Create `ui/experience/` as an Experience Platform layer that owns all cross-cutting interaction, workflow, layout, and usability concerns. The platform sits between the Command Center views and the user, providing:

1. **Animation Manager** — fade, slide, scale, bounce, pulse animations via QPropertyAnimation abstraction
2. **Layout Engine** — responsive grid with breakpoints, panel containers, persistent layout save/load
3. **Navigation Engine** — route registration, history (back/forward), breadcrumb generation
4. **Interaction Engine** — hover effects, tooltips, drag-drop configuration, cursor management
5. **Shortcut Manager** — centralized keyboard shortcut registration with context scoping
6. **Command Palette Engine** — unified command registry with search, categories, execute
7. **Search Provider** — pluggable global search with relevance scoring
8. **Notification Center** — toast notifications, notification history, priority-based styling
9. **Loading State Manager** — skeleton screens, spinner overlays, progress indicators
10. **Empty State Manager** — configurable empty states with icons, CTAs, show/hide lifecycle
11. **Focus Mode** — distraction-free mode hiding chrome elements
12. **Window Layout Manager** — window geometry persistence, state save/restore
13. **Workspace Manager** — multi-workspace support with stacked widget routing
14. **Workflow Engine** — multi-step guided workflows with validation and dialog
15. **Theme Transition Manager** — animated theme transitions

## Architecture

```
ui/experience/
├── experience_manager.py           # Top-level orchestrator (owns all engines)
├── animation_manager.py            # QPropertyAnimation abstraction
├── layout_engine.py                # ResponsiveGrid, PanelContainer, LayoutConfig
├── navigation_engine.py            # Route registry, history, breadcrumbs
├── interaction_engine.py           # HoverWatcher, TooltipManager, drag-drop
├── shortcut_manager.py             # Centralized Shortcut registry
├── command_palette_engine.py       # CommandItem registry + CommandPaletteDialog
├── search_provider.py              # Pluggable SearchProvider with relevance scoring
├── notification_center.py          # Toast notifications + history
├── loading_state_manager.py        # SkeletonWidget, LoadingOverlay, ProgressIndicator
├── empty_state_manager.py          # EmptyStateWidget with configurable CTA
├── focus_mode.py                   # Distraction-free mode toggle
├── window_layout_manager.py        # Window geometry persistence
├── workspace_manager.py            # Multi-workspace management
├── workflow_engine.py              # Multi-step guided workflows
└── theme_transition_manager.py     # Animated theme transitions
```

## Integration with Command Center

The ExperienceManager is instantiated by the main application bootstrap alongside the Command Center. It provides:
- `register_default_page_routes()` — registers Command Center pages as navigation routes
- `register_default_command_palette_pages()` — adds page navigation commands to the palette
- `propagate_data()` — forwards data updates from the Command Center to the experience layer

## Key Decisions

- **No business logic** — all engines are pure UX infrastructure; no domain knowledge
- **No hardcoded colors** — all visual tokens imported from `ui.command_center.theme.C`
- **Event-driven architecture** — Qt Signals used throughout for loose coupling
- **Lazy registration** — engines start empty; routes/shortcuts/commands registered by consumers
- **Deterministic** — no randomness; all animations are fixed-duration transitions
- **No AI/LLM** — all functionality is deterministic and reproducible

## Consequences

Positive:
- All cross-cutting UX concerns centralized in one layer
- Command Center pages can remain focused on data display
- Persistent layouts enable workspace continuity
- Keyboard-first workflow via ShortcutManager + CommandPaletteEngine
- 300+ tests validate all engine behaviors independently

Negative:
- ExperienceManager is a singleton-like orchestrator (single instance per app)
- Some features (focus mode, workspace management) require explicit widget registration
- Theme transitions depend on animation engine availability

## File Impact

- 16 new source files in `ui/experience/`
- 1 conftest + 16 test files (301 tests)
- No modifications to existing business logic or shared modules
- Integration via `main_window.py` bootstrap only
