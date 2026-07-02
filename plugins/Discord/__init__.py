from sdk import Plugin, PluginManifest


class DiscordPlugin(Plugin):
    manifest = PluginManifest(
        name="discord",
        version="1.0.0",
        description="Discord bot integration for notifications and commands",
        author="NEXUS",
        requires_capabilities=["notifications.send"],
    )

    async def on_load(self) -> None:
        ...

    async def on_unload(self) -> None:
        ...
