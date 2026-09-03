import discord
from discord.ext import commands
from discord import app_commands

from api_client import ApiClient
from bot_app import BotApp
from exceptions.api_error import ApiError


class LinkCommands(commands.Cog):
    def __init__(self, bot: BotApp):
        self.bot = bot

    @app_commands.command(name="link_fix", description="Fix embeds for links")
    async def link_fix(self, interaction: discord.Interaction, link: str):
        payload = {
            "text": link
        }

        try:
            data = await ApiClient(f"{self.bot.config.api_base_url}/rewriter/rewrite", payload).post_json(interaction, expected="dict")
        except ApiError as e:
            await e.send(interaction)
            return

        if not data:
            await interaction.followup.send("API returned unexpected data.", ephemeral=True)
            return

        await interaction.followup.send(f"<{data.get('rewritten', 'Sorry, could not rewrite the link.')}>")

async def setup(bot):
    await bot.add_cog(LinkCommands(bot))