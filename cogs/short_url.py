import discord
from discord import app_commands
from discord.ext import commands

from api_client import ApiClient
from bot_app import BotApp
from exceptions.api_error import ApiError

class ShortUrlCommands(commands.Cog):
    def __init__(self, bot: BotApp):
        self.bot = bot

    @staticmethod
    def _actor_payload(interaction: discord.Interaction) -> dict[str, object]:
        return {
            "discord_id": str(interaction.user.id),
            "username": interaction.user.name,
        }

    @app_commands.command(name="short_new", description="Short new url")
    @app_commands.describe(
        long_url="Target (long) URL to shorten",
        slug="Optional custom slug (e.g. abc1). If empty, the API will generate one.",
        name="Optional name for the link",
    )
    async def short_new( self, interaction: discord.Interaction, long_url: str, slug: str | None = None, name: str | None = None) -> None:
        long_url = (long_url or "").strip()
        slug = (slug or "").strip()
        name = (name or "").strip()

        if not long_url:
            await interaction.response.send_message("`long_url` is required.", ephemeral=True)
            return

        payload = {
            **self._actor_payload(interaction),
            "long_url": long_url,
        }
        if slug:
            payload["slug"] = slug
        if name:
            payload["name"] = name

        try:
            data = await ApiClient(f"{self.bot.config.api_base_url}/api/dc-urlshortener/create/", payload).post_json(interaction, expected="dict")
        except ApiError as e:
            await e.send(interaction)
            return

        created_short_url = data.get("short_url")
        created_slug = data.get("slug")
        if not created_short_url or not created_slug:
            await interaction.followup.send("Created, but API returned incomplete data.", ephemeral=True)
            return

        returned_name = data.get("name")
        extra = f" (name: {returned_name})" if returned_name else ""
        await interaction.followup.send(f"Created: <{created_short_url}> (slug: `{created_slug}`){extra}")


    @app_commands.command(name="short_list", description="List all shortened URLs by you")
    async def short_list(self, interaction: discord.Interaction) -> None:
        payload = self._actor_payload(interaction)

        try:
            data = await ApiClient(f"{self.bot.config.api_base_url}/api/dc-urlshortener/list/", payload).post_json(interaction, expected="list")
        except ApiError as e:
            await e.send(interaction)
            return

        if not data:
            await interaction.followup.send("No shortened URLs found.")
            return

        lines: list[str] = []
        for entry in data:
            if not isinstance(entry, dict):
                continue

            short_url = entry.get("short_url")
            long_url = entry.get("long_url")
            slug = entry.get("slug")
            name = entry.get("name")

            if not short_url or not long_url:
                continue

            lines.append(f"<{short_url}> -> <{long_url}> ({name or slug})")

        message = "\n".join(lines) if lines else "No shortened URLs found."
        await interaction.followup.send(message)

    @app_commands.command(name="short_delete", description="Delete one of your shortened URLs by name or slug")
    @app_commands.describe(name="name or slug of the shortened URL to delete (name is prioritized)")
    @app_commands.describe(slug="slug of the shortened URL to delete (name is prioritized)")
    async def short_delete(self, interaction: discord.Interaction, name: str | None = None, slug: str | None = None) -> None:
        name_value = (name or "").strip()
        slug_value = (slug or "").strip()

        if not name_value and not slug_value:
            await interaction.response.send_message("You must provide either `name` or `slug`.", ephemeral=True)
            return

        payload = self._actor_payload(interaction)

        if name is not None:
            payload["name"] = name
        if slug is not None:
            payload["slug"] = slug
        elif name:
            payload["slug"] = name

        try:
            await ApiClient(f"{self.bot.config.api_base_url}/api/dc-urlshortener/delete/", payload).post(interaction)
        except ApiError as e:
            await e.send(interaction)
            return

        await interaction.followup.send(f"`{name_value or slug_value}` deleted successfully.")

async def setup(bot: BotApp) -> None:
    await bot.add_cog(ShortUrlCommands(bot))