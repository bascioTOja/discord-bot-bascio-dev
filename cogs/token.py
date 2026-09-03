import discord
from discord.ext import commands
from discord import app_commands

from bot_app import BotApp


class TokenCommands(commands.Cog):
    def __init__(self, bot: BotApp):
        self.bot = bot

    @app_commands.command(name="token_register", description="Register token to use tools.bascio.dev api")
    async def token_register(self, interaction: discord.Interaction, api_token: str):
        message = self.bot.db.register_token(str(interaction.user.id), interaction.user.global_name or interaction.user.name, api_token)

        await interaction.response.send_message(message)

    @app_commands.command(name="token_unregister", description="Unregister token from tools.bascio.dev api")
    async def token_unregister(self, interaction: discord.Interaction):
        message = self.bot.db.unregister_token(str(interaction.user.id))

        await interaction.response.send_message(message)

async def setup(bot):
    await bot.add_cog(TokenCommands(bot))