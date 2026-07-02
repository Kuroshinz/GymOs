from sdk import Plugin, PluginManifest


class TelegramPlugin(Plugin):
    manifest = PluginManifest(
        name="telegram",
        version="1.0.0",
        description="Telegram bot integration for notifications and commands",
        author="NEXUS",
        requires_capabilities=["notifications.send"],
    )

    async def on_load(self) -> None:
        ...

    async def on_unload(self) -> None:
        ...
