import discord
from discord.ext import commands
from discord import app_commands, ui

from api_client import ApiClient
from bot_app import BotApp
from exceptions.api_error import ApiError


class AskLLMCommands(commands.Cog):
    def __init__(self, bot: BotApp):
        self.bot = bot

    @app_commands.command(name="ask_llm", description="Ask the LLM a question")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def ask_llm(self, interaction: discord.Interaction, prompt: str):
        auth_token = self.bot.db.get_token(str(interaction.user.id))
        payload = {
            "prompt": prompt
        }

        try:
            data = await ApiClient(f"{self.bot.config.api_base_url}/ask-llm", payload, auth_token=auth_token).post_json(interaction, expected="dict")
        except ApiError as e:
            await e.send(interaction)
            return

        if not data:
            await interaction.followup.send("API returned unexpected data.", ephemeral=True)
            return

        await interaction.followup.send(view=LMMAnswer(prompt=prompt, answer=data.get("answer", "No answer provided.")))

class LMMAnswer(ui.LayoutView):
    def __init__(self, prompt: str, answer: str):
        super().__init__()

        container = ui.Container(accent_color=0x5865F2)
        container.add_item(ui.TextDisplay(content=prompt))

        answer = answer.replace("\n", "\n> ")
        container.add_item(ui.TextDisplay(content=f"> {answer}"))

        self.add_item(container)

async def setup(bot):
    await bot.add_cog(AskLLMCommands(bot))