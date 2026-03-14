import logging

import discord

from dataclasses import dataclass
from typing import Optional
from discord.ext import commands

from config import Config

logger = logging.getLogger(__name__)

@dataclass
class Channels:
    announce: Optional[discord.abc.Messageable] = None
    debug: Optional[discord.abc.Messageable] = None

class BotApp(commands.Bot):
    def __init__(self, config: Config):
        super().__init__(command_prefix="/", intents=discord.Intents.all())

        self.config = config
        self.channels = Channels()
        logger.info("BotApp initialized")

    async def setup_hook(self):
        #TODO: get from files
        await self.load_extension('cogs.test')
        logger.info("Loaded 'cogs.test' extension")

        await self.load_extension('cogs.short_url')
        logger.info("Loaded 'cogs.short_url' extension")

    async def on_ready(self):
        logger.info(f"Logged in as {self.user}")

        self.channels.announce = self.get_channel(self.config.announce_channel_id)
        self.channels.debug = self.get_channel(self.config.debug_channel_id)
        logger.info(
            "Channels resolved: announce=%s debug=%s",
            getattr(self.channels.announce, "id", None),
            getattr(self.channels.debug, "id", None),
        )

        await self.tree.sync()
