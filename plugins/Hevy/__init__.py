from sdk import Plugin, PluginManifest


class HevyPlugin(Plugin):
    manifest = PluginManifest(
        name="hevy",
        version="1.0.0",
        description="Hevy workout tracking integration",
        author="NEXUS",
        requires_capabilities=["workout.read", "workout.write"],
    )

    async def on_load(self) -> None:
        ...

    async def on_unload(self) -> None:
        ...
