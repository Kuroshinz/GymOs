# GymOS Command Center — UX Guidelines

## Theme

The Command Center uses the existing GymOS dark theme:

| Token | Value | Usage |
|-------|-------|-------|
| `C.BG` | `#0F172A` | Page background |
| `C.CARD_BG` | `#1E293B` | Card backgrounds |
| `C.BORDER` | `#334155` | Card borders |
| `C.ACCENT` | `#818CF8` | Primary accent (indigo) |
| `C.TEXT_PRIMARY` | `#F1F5F9` | Primary text |
| `C.TEXT_SECONDARY` | `#94A3B8` | Secondary text |
| `C.TEXT_MUTED` | `#64748B` | Muted labels |
| `C.TEXT_SUCCESS` | `#4ADE80` | Positive indicators |
| `C.TEXT_WARN` | `#FBBF24` | Warning indicators |
| `C.TEXT_DANGER` | `#F87171` | Critical indicators |

## Layout

- **Sidebar**: Fixed 220px width, dark (`#0B1120`), grouped sections with icons
- **Top bar**: Breadcrumb (left) + Quick Search (right, 320px)
- **Content**: Scrollable areas per page with 32px horizontal/24px vertical padding
- **Widget spacing**: 12px between cards, 16px between sections

## Component Structure

All widgets extend `DashboardCard` from `ui.dashboard.dashboard_widgets.base_card`:
- Consistent dark card styling (`#1E293B` bg, `#334155` border, 12px radius)
- Uppercase title label with muted color (`#94A3B8`, 11px, 600 weight)
- Optional badge for live/status indicators
- Content area via `add_content()` / `add_layout()`

## Widget Patterns

Each widget follows this contract:
1. `__init__()` — build UI structure with empty/default state
2. `set_data(model_data)` — populate with typed model
3. `update_data(data)` — called by page with attribute access (`getattr`)

## Navigation Patterns

- **Sidebar click**: emits `page_changed(page_id)` → CommandCenter._navigate()
- **Quick Search**: filters by keywords, emits `navigated(page_id)`
- **Command Palette**: Ctrl+K opens modal, `command_selected(cmd)` executes

## Responsive Behavior

- Pages use `QScrollArea` for content overflow
- Cards have `QSizePolicy.Expanding` for flexible sizing
- Grid panels adjust with `set_columns()`

## Event-Driven Updates

- `CommandCenterController` subscribes to 12 domain events
- Section-level refresh avoids full-page reloads
- Auto-refresh timer: 60-second interval
