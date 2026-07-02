from sdk import Plugin, PluginManifest


class SpotifyPlugin(Plugin):
    manifest = PluginManifest(
        name="spotify",
        version="1.0.0",
        description="Spotify music integration for workout playlists",
        author="NEXUS",
        requires_capabilities=["network.http", "media.playback"],
    )

    async def on_load(self) -> None:
        ...

    async def on_unload(self) -> None:
        ...
