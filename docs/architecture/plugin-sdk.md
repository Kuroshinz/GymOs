# Plugin SDK

## Contract

Every plugin must:

1. **Extend** `sdk.Plugin`
2. **Define** `manifest: PluginManifest`
3. **Implement** `on_load()` and `on_unload()`

## Lifecycle

```
Registered → on_load() → on_enable() → ACTIVE
                                        → on_disable() → on_unload() → Removed
```

## Manifest Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Unique identifier |
| `version` | Yes | SemVer |
| `description` | No | Human-readable |
| `author` | No | Creator |
| `dependencies` | No | Other plugin names |
| `requires_capabilities` | No | Required permissions |

## Capabilities

Capabilities grant access to platform features:

| Capability | Description |
|------------|-------------|
| `network.http` | HTTP requests |
| `notifications.send` | Push notifications |
| `workout.read` | Read workout data |
| `workout.write` | Create/update workouts |
| `nutrition.write` | Log meals |
| `media.playback` | Control media |
| `storage.local` | Local file access |
| `ui.widget` | Register UI widgets |

## Event Hooks

Plugins can subscribe to events:

```python
async def on_load(self):
    self.event_bus = nexus.platform.event_bus
    self.event_bus.on("workout.created", self.handle_workout)
```

## Configuration

Plugins receive config via `self.config`:

```python
class MyPlugin(Plugin):
    async def on_load(self):
        api_key = self.config.credentials.get("api_key")
        enabled = self.config.enabled
```

Configuration is loaded from `config/plugins/<name>.json`.
