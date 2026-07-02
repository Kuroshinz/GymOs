from sdk import Plugin, PluginManifest


class CronometerPlugin(Plugin):
    manifest = PluginManifest(
        name="cronometer",
        version="1.0.0",
        description="Cronometer nutrition tracking integration",
        author="NEXUS",
        requires_capabilities=["nutrition.write"],
    )

    async def on_load(self) -> None:
        ...

    async def on_unload(self) -> None:
        ...
