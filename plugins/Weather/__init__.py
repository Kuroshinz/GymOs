from sdk import Plugin, PluginManifest


class WeatherPlugin(Plugin):
    manifest = PluginManifest(
        name="weather",
        version="1.0.0",
        description="Weather data integration for workout planning",
        author="NEXUS",
        requires_capabilities=["network.http"],
    )

    async def on_load(self) -> None:
        ...

    async def on_unload(self) -> None:
        ...
