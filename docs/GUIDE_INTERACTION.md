# GymOS Interaction Guidelines

## Hover States

All interactive elements MUST provide visual hover feedback:

| Element | Hover Behavior | Implementation |
|---------|---------------|----------------|
| Sidebar buttons | Background color change to `C.CARD_BG`, cursor to pointing hand | `InteractionEngine.register_hover()` |
| Cards | Border color change to `C.BORDER_HOVER`, subtle scale | CSS `.card:hover { border-color: ... }` |
| Command palette items | Highlight with `C.ACCENT` background | Built-in `QListWidget::item:selected` |
| Buttons | Background lighten, cursor to pointing hand | CSS `QPushButton:hover { ... }` |
| Toast notifications | Pointer cursor, dismiss button visible | `NotificationToast` cursor override |

## Cursor Mapping

| Context | Cursor |
|---------|--------|
| Default interactive | `PointingHandCursor` |
| Dragging | `ClosedHandCursor` |
| Resizing | `SizeHorCursor` / `SizeVerCursor` |
| Text input | `IBeamCursor` |
| Not allowed | `ForbiddenCursor` |

## Keyboard Navigation

All functionality MUST be accessible via keyboard:

- **Tab** — Move focus between interactive elements
- **Enter/Space** — Activate focused element
- **Escape** — Close dialogs, exit focus mode
- **Ctrl+K** — Open command palette
- **Ctrl+Shift+F** — Toggle focus mode
- **Alt+Left/Right** — Navigate back/forward
- **Ctrl+R** — Refresh current view

## Drag and Drop

Widgets can be registered as drag sources or drop targets:

```python
engine.interaction.register_drag_drop(DragDropConfig(
    widget_id="card-1",
    drag_enabled=True,
    mime_type="application/x-gymos-card",
))
```

## Animation Guidelines

| Use Case | Animation | Duration |
|----------|-----------|----------|
| Page transitions | Fade in/out | 300ms |
| Modal open | Scale + fade | 300ms |
| Toast appear | Slide down + fade | 150ms |
| Hover feedback | Immediate style change | 0ms |
| Loading skeleton | Pulse opacity | 1.5s loop |
| Theme transition | Cross-fade | 500ms |
