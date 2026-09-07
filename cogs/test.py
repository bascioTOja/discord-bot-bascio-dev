import discord
from discord.ext import commands
from discord import app_commands

from bot_app import BotApp


class TestCommands(commands.Cog):
    def __init__(self, bot: BotApp):
        self.bot = bot

    @app_commands.command(
        name="ping",
        description="Test command to check if the bot is responsive",
    )
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! latency: {latency}ms")

async def setup(bot):
    await bot.add_cog(TestCommands(bot))