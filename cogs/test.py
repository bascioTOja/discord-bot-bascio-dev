import discord
from discord.ext import commands
from discord import app_commands

class TestCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Test command to check if the bot is responsive")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! latency: {latency}ms")

async def setup(bot):
    await bot.add_cog(TestCommands(bot))