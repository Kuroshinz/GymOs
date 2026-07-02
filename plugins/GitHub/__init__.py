from sdk import Plugin, PluginManifest


class GitHubPlugin(Plugin):
    manifest = PluginManifest(
        name="github",
        version="1.0.0",
        description="GitHub integration for project tracking and code analysis",
        author="NEXUS",
        requires_capabilities=["network.http"],
    )

    async def on_load(self) -> None:
        ...

    async def on_unload(self) -> None:
        ...
