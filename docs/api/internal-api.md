# Internal API Reference

## Core Services

### EventBus (`core.event_bus`)

```python
bus = EventBus()

bus.use(middleware)          # Add middleware
bus.on(event, handler)       # Subscribe (also usable as decorator)
bus.once(event, handler)     # Subscribe for one invocation
bus.off(event, handler)      # Unsubscribe
await bus.emit(name, data, source="", correlation_id="")  # Publish
bus.clear()                  # Remove all handlers
```

### Container (`core.di`)

```python
container = Container()

container.register(name, instance)    # Register singleton instance
container.register_factory(name, fn, lifetime)  # Factory
container.alias(alias, target)        # Create alias
container.resolve(name)               # Get by name
container.get(ClassType)              # Get by type
await container.dispose()             # Cleanup
```

### PluginManager (`core.plugin`)

```python
pm = PluginManager()

pm.add_search_path(path)          # Add plugin directory
pm.register(plugin)               # Register plugin instance
pm.discover(path)                 # Auto-discover plugins
await pm.load_all()               # Load all plugins
await pm.unload_all()             # Unload all
```

### ThemeManager (`core.theme`)

```python
tm = ThemeManager()

tm.register(theme)                # Add custom theme
tm.activate(name)                 # Switch theme
tm.toggle_dark_mode()             # Toggle dark/light
theme = tm.current                # Get active theme

# Access tokens
theme.current_colors.primary
theme.typography.h1
theme.spacing.lg
```

### Logger (`core.logger`)

```python
logger = Logger()

logger.setup(name="nexus", level=logging.INFO, log_file="path")
logger.info("message")
logger.error("error")
```

### Scheduler (`core.scheduler`)

```python
scheduler = Scheduler()

scheduler.add("task_name", async_func, interval_seconds)
await scheduler.start_all()
await scheduler.stop_all()
```

## Engine Events

Engines communicate via EventBus:

| Event | Data | Produced By |
|-------|------|-------------|
| `workout.created` | `{id, name, started_at}` | Any module |
| `workout.completed` | `{workout_id, duration, volume, exercises}` | WorkoutEngine |
| `nutrition.meal_logged` | `{meal, calories, protein, date}` | NutritionEngine |
| `recovery.sleep_logged` | `{duration, quality, date}` | RecoveryEngine |
| `analytics.updated` | `{type, metrics}` | AnalyticsEngine |
| `settings.changed` | `{key, old_value, new_value}` | Settings |
| `plugin.loaded` | `{name, version}` | PluginManager |
| `platform.started` | `{}` | Platform |
| `platform.shutting_down` | `{}` | Platform |
