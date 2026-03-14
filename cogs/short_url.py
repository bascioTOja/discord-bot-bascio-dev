from json import JSONDecodeError

import discord
from discord.ext import commands
from discord import app_commands

import httpx

from bot_app import BotApp

#TODO: extract common API call logic to separate class, errors return by custom ApiError exception

class ShortUrlCommands(commands.Cog):
    def __init__(self, bot: BotApp):
        self.bot = bot

    @app_commands.command(name="short_new", description="Short new url")
    @app_commands.describe(
        long_url="Target (long) URL to shorten",
        slug="Optional custom slug (e.g. abc1). If empty, the API will generate one.",
        name="Optional name/description for the link",
    )
    async def short_new( self, interaction: discord.Interaction, long_url: str, slug: str | None = None, name: str | None = None):
        long_url = (long_url or "").strip()
        slug = (slug or "").strip()
        name = (name or "").strip()

        if not long_url:
            await interaction.response.send_message("`long_url` is required.", ephemeral=True)

            return

        payload: dict[str, object] = {
            "discord_id": str(interaction.user.id),
            "username": interaction.user.name,
            "long_url": long_url,
        }
        if slug:
            payload["slug"] = slug
        if name:
            payload["name"] = name

        endpoint = f"{self.bot.config.api_base_url}/api/dc-urlshortener/create/"

        # Defer to avoid Discord timeouts on slow API responses.
        await interaction.response.defer(thinking=True)

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(endpoint, json=payload)
        except httpx.RequestError as e:
            await interaction.followup.send(f"Could not reach the API: `{type(e).__name__}`.", ephemeral=True)

            return

        try:
            data: dict = resp.json()
        except JSONDecodeError as e:
            await interaction.followup.send(f"JSON decoding error.", ephemeral=True)
            return

        if resp.status_code in (200, 201):
            short_url = data["short_url"]
            returned_slug = data["slug"]
            returned_name = data.get("name")

            extra = f" (name: {returned_name})" if returned_name else ""
            await interaction.followup.send(f"Created: <{short_url}> (slug: `{returned_slug}`){extra}")
            return

        # errors
        detail = data.get("detail") if isinstance(data, dict) else None
        detail_txt = f" ({detail})" if detail else ""

        if resp.status_code == 400:
            await interaction.followup.send(f"Invalid input{detail_txt}.", ephemeral=True)
            return

        if resp.status_code == 409:
            await interaction.followup.send(f"Conflict{detail_txt}. If you provided `slug`, try another one.", ephemeral=True)
            return

        await interaction.followup.send(f"API returned {resp.status_code}{detail_txt}.", ephemeral=True)

    @app_commands.command(name="short_list", description="List all shortened URLs by you")
    async def short_list( self, interaction: discord.Interaction):
        payload: dict[str, object] = {
            "discord_id": str(interaction.user.id),
            "username": interaction.user.name,
        }

        endpoint = f"{self.bot.config.api_base_url}/api/dc-urlshortener/list/"

        # Defer to avoid Discord timeouts on slow API responses.
        await interaction.response.defer(thinking=True)

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(endpoint, json=payload)
        except httpx.RequestError as e:
            await interaction.followup.send(f"Could not reach the API.", ephemeral=True)

            return

        try:
            data: dict = resp.json()
        except JSONDecodeError as e:
            await interaction.followup.send(f"JSON decoding error.", ephemeral=True)

            return

        if resp.status_code in (200, 201):
            response = ""
            for index, short_url_data in enumerate(data):
                short_url = short_url_data.get("short_url")
                long_url = short_url_data.get("long_url")
                slug = short_url_data.get("slug")
                name = short_url_data.get("name")

                response += f"\n<{short_url}> -> <{long_url}> ({name or slug})"


            await interaction.followup.send(response)
            return

        # errors
        detail = data.get("detail") if isinstance(data, dict) else None
        detail_txt = f" ({detail})" if detail else ""

        if resp.status_code == 400:
            await interaction.followup.send(f"Invalid input{detail_txt}.", ephemeral=True)
            return

        if resp.status_code == 409:
            await interaction.followup.send(f"Conflict{detail_txt}. If you provided `slug`, try another one.", ephemeral=True)
            return

        await interaction.followup.send(f"API returned {resp.status_code}{detail_txt}.", ephemeral=True)

    @app_commands.command(name="short_delete", description="Delete one of your shortened URLs by name or slug")
    @app_commands.describe(name="name or slug of the shortened URL to delete (name is prioritized)")
    @app_commands.describe(slug="slug of the shortened URL to delete (name is prioritized)")
    async def short_delete(self, interaction: discord.Interaction, name: str | None = None, slug: str | None = None):
        if name is None and slug is None:
            await interaction.response.send_message("You must provide either `name` or `slug`.", ephemeral=True)

            return

        payload: dict[str, object] = {
            "discord_id": str(interaction.user.id),
            "username": interaction.user.name,
        }

        if name is not None:
            payload["name"] = name

        if slug is not None:
            payload["slug"] = slug
        elif name:
            payload["slug"] = name

        endpoint = f"{self.bot.config.api_base_url}/api/dc-urlshortener/delete/"

        # Defer to avoid Discord timeouts on slow API responses.
        await interaction.response.defer(thinking=True)

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                resp = await client.post(endpoint, json=payload)
        except httpx.RequestError as e:
            await interaction.followup.send(f"Could not reach the API.", ephemeral=True)

            return

        try:
            data: dict = resp.json()
        except JSONDecodeError as e:
            await interaction.followup.send(f"JSON decoding error.", ephemeral=True)

            return

        if resp.status_code in (200, 201):
            await interaction.followup.send(f"{slug} deleted successfully.")

            return

        # errors
        detail = data.get("detail") if isinstance(data, dict) else None
        detail_txt = f" ({detail})" if detail else ""

        if resp.status_code == 400:
            await interaction.followup.send(f"Invalid input{detail_txt}.", ephemeral=True)
            return

        if resp.status_code == 409:
            await interaction.followup.send(f"Conflict{detail_txt}. If you provided `slug`, try another one.", ephemeral=True)
            return

        await interaction.followup.send(f"API returned {resp.status_code}{detail_txt}.", ephemeral=True)

async def setup(bot: BotApp):
    await bot.add_cog(ShortUrlCommands(bot))