from typing import Union
import discord
from discord import Message, Embed
from discord.ext import commands
from discord.ext.commands import AutoShardedBot, Context
from discord_slash import SlashContext, ComponentContext
import logging
import os
from datetime import datetime
from config import BotConfig
from utils.custom_slash_command import CustomSlashCommand
from utils import Counter, fakeDefer
from utils.errors import handle_error
from utils.game_data import GameDataServer
from utils.state_manger import StateManger, State

__author__ = "IanDesuyo"
__version__ = "3.1.8"


class AIKyaru(AutoShardedBot):
    """
    A Discord bot for Princess Connect Re:Dive.

    Kyaru best waifu <3
    """

    def __init__(self):
        self.__version__ = __version__
        self.logger = logging.getLogger("AIKyaru")
        self.logger.info("Starting...")
        self.config = BotConfig()
        self.gameData = GameDataServer()
        self.counter = Counter()
        self.stateManger = StateManger(self.config.get(["MONGODB_URL"]))
        super().__init__(
            command_prefix=commands.when_mentioned_or(self.config.get(["prefix"])),
            case_insensitive=True,
            help_command=None,
        )

    def init_(self):
        """
        Load Cogs after :class:`SlashCommand` loaded.

        Raises:
            ExtensionAlreadyLoaded: Extension already loaded.
        """
        for i in self.config.get(["cogs"]):
            try:
                self.load_extension(i)
                self.logger.info(f"{i} loaded.")
            except commands.ExtensionAlreadyLoaded:
                self.logger.warning(f"{i} already loaded.")
            except Exception as e:
                self.logger.error(f"Error when loading {i}.")
                raise e

    async def on_ready(self):
        if not hasattr(self, "uptime"):
            # Only run once
            self.uptime = datetime.utcnow()
            await self.config.update_gacha_emojis(self)
            await self.change_presence(
                status=discord.Status.online,
                activity=discord.Activity(
                    type=self.config.get(["activity", "type"]),
                    name=f"{self.config.get(['activity','prefix'])}{self.config.get(['activity','default_text'])}",
                ),
            )

        self.logger.info(f"Ready: {self.user} (ID: {self.user.id})")

    async def on_shard_ready(self, shard_id: int):
        self.logger.info(f"Shard ready, ID: {shard_id}")

    async def on_shard_disconnect(self, shard_id: int):
        self.logger.warning(f"Shard disconnected, ID: {shard_id}")

    async def close(self):
        for i in list(self.extensions):
            self.unload_extension(i)
            self.logger.info(f"{i} unloaded.")
        await super().close()

    async def send_debug(self, content: str = None, embed: Embed = None):
        await self.get_channel(self.config.get(["DEBUG_CHANNEL"])).send(content=content, embed=embed)
        if content:
            self.logger.warning(f"Debug message sent: {content}")
        elif embed:
            self.logger.warning(f"Debug message sent: {embed.title}")

    async def on_message(self, message: Message):
        """
        Overwrite :func:`on_message` to inject :class:`State`.
        """
        if message.author.bot:
            return

        self.counter.add("message_received")
        ctx = await self.get_context(message)
        if ctx.command:
            ctx.state = State(self.stateManger, ctx)
            ctx.defer = fakeDefer  # Avoid errors when using defer()
            self.counter.add(ctx.command.name)
            await self.invoke(ctx)

    async def invoke_slash_command(self, func, ctx: SlashContext, args):
        """
        Overwrite :func:`slash_command` to inject :class:`State`.
        """
        ctx.state = State(self.stateManger, ctx)
        self.counter.add("slash_received")
        self.counter.add("slash_" + ctx.name)
        await func.invoke(ctx, **args)

    async def invoke_component_callback(self, func, ctx: ComponentContext):
        """
        Overwrite :func:`invoke_component_callback` to inject :class:`State`.
        """
        ctx.state = State(self.stateManger, ctx)
        self.counter.add("component_received")
        self.counter.add("component_" + ctx.custom_id)
        await func.invoke(ctx)

    async def on_slash_command_error(self, ctx: SlashContext, error):
        await handle_error(self, ctx, error)

    async def on_component_callback_error(self, ctx: ComponentContext, error):
        await handle_error(self, ctx, error)

    async def on_command_error(self, ctx: Union[Context, SlashContext], error):
        await handle_error(self, ctx, error)


if __name__ == "__main__":
    log_handlers = [logging.StreamHandler()]
    if not os.environ.get("NO_LOG_FILE"):
        log_handlers.append(logging.FileHandler("bot.log"))

    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s][%(asctime)s][%(name)s] %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
        handlers=log_handlers,
    )

    for folder in ["./gameDB"]:
        os.makedirs(folder, exist_ok=True)

    bot = AIKyaru()
    slash = CustomSlashCommand(bot, sync_commands=True, sync_on_cog_reload=False)
    bot.init_()

    bot.run(os.environ.get("BOT_TOKEN"))
