import logging
from main import AIKyaru
from typing import Union
from discord.ext import commands
from discord.ext.commands import Context
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from aiohttp import ClientSession, ClientTimeout
import asyncio


class NewsForward(commands.Cog):
    def __init__(self, bot: AIKyaru):
        self.bot = bot
        self.logger = logging.getLogger("AIKyaru.NewsForward")
        self.apiUrl = "https://randosoru.me/api/newsForward"
        self.session = ClientSession(headers={"User-Agent": "AIKyaru v3"}, timeout=ClientTimeout(total=10))

    def cog_unload(self):
        asyncio.get_event_loop().run_until_complete(self.session.close())

    #
    # Functions
    #
    async def get_webhook(self, ctx: Union[Context, SlashContext], create=True):
        webhooks = await ctx.channel.webhooks()
        webhook = None

        for i in webhooks:
            if i.user.id == self.bot.user.id:
                webhook = i
                break

        if not webhook and create:
            webhook = await ctx.channel.create_webhook(
                name="公告轉發", reason=f"By {ctx.author.name}#{ctx.author.discriminator}"
            )

        return webhook

    async def set(self, id: int, token: str, tw: bool = False, jp: bool = False):
        async with self.session.post(
            self.apiUrl, json={"id": id, "token": token, "tw": tw, "jp": jp, "custom": False}
        ) as resp:
            data = await resp.json()

        self.logger.info(f"set tw:{tw} jp:{jp}")
        if resp.status != 200:
            self.logger.error(f"API responsed with {resp.status}")
            self.logger.error(f"Webhook id:{id} token:{token} tw:{tw} jp:{jp}")
            self.logger.error(data)
            raise ValueError(f"NewsForward {resp.status}")

        return data

    #
    # Commands
    #
    @commands.group(name="newsforward", hidden=True)
    @commands.bot_has_permissions(manage_webhooks=True)
    @commands.guild_only()
    async def cmd_newsforward(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            return

    @cmd_newsforward.command(name="subscribe", description="訂閱公告轉發")
    async def cmd_subscribe(self, ctx: Context, tw: bool = False, jp: bool = False):
        await self._subscribe(ctx, tw, jp)

    @cog_ext.cog_subcommand(
        base="newsforward",
        name="subscribe",
        description="訂閱公告轉發",
        options=[
            create_option(name="台版", description="是否訂閱台版公告轉發", option_type=5, required=True),
            create_option(name="日版", description="是否訂閱日版公告轉發", option_type=5, required=True),
        ],
        connector={"台版": "tw", "日版": "jp"},
    )
    @commands.bot_has_permissions(manage_webhooks=True)
    @commands.guild_only()
    async def cog_subscribe(self, ctx: SlashContext, tw: bool, jp: bool):
        await self._subscribe(ctx, tw, jp)

    async def _subscribe(self, ctx: Union[Context, SlashContext], tw: bool, jp: bool):
        if not tw and not jp:
            return self._unsubscribe(ctx)

        await ctx.defer()
        webhook = await self.get_webhook(ctx)
        await self.set(webhook.id, webhook.token, tw, jp)
        await ctx.send(":white_check_mark: 訂閱成功")

    @cmd_newsforward.command(name="unsubscribe", description="取消訂閱公告轉發")
    async def cmd_unsubscribe(self, ctx: Context):
        await self._unsubscribe(ctx)

    @cog_ext.cog_subcommand(
        base="newsforward",
        name="unsubscribe",
        description="取消訂閱公告轉發",
    )
    @commands.bot_has_permissions(manage_webhooks=True)
    @commands.guild_only()
    async def cog_unsubscribe(self, ctx: SlashContext):
        await self._unsubscribe(ctx)

    async def _unsubscribe(self, ctx: Union[Context, SlashContext]):
        await ctx.defer()
        webhook = await self.get_webhook(ctx, False)
        if not webhook:
            return await ctx.send(":warning: 尚未訂閱")
        await self.set(webhook.id, webhook.token, False, False)
        await webhook.delete()
        await ctx.send(":white_check_mark:  已取消訂閱")


def setup(bot):
    bot.add_cog(NewsForward(bot))
