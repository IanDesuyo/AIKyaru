import logging
from utils.errors import create_debug_embed
from main import AIKyaru
import discord
from discord.ext import commands
from discord.ext.commands import Context
import utils
import asyncio
import uuid


class Admin(commands.Cog):
    def __init__(self, bot: AIKyaru):
        self.bot = bot
        self.logger = logging.getLogger("AIKyaru.Admin")

    @commands.command(brief="呼叫凱留", aliases=["呼叫凱留"], usage="<訊息(選填)>", hidden=True)
    async def callHelp(self, ctx: Context, *, msg: str = None):
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) == "\u2705"

        is_guild = isinstance(ctx.channel, discord.TextChannel)
        if is_guild:
            message = await ctx.send("請點擊下方 :white_check_mark: 來同意機器人蒐集必要資料以供除錯")
            await message.add_reaction("\u2705")

            try:
                await self.bot.wait_for("reaction_add", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                return await message.delete()

            await message.edit(content="獲取資料中...")
            await message.clear_reactions()
        else:
            message = await ctx.send("獲取資料中...")

        tracking_uuid = str(uuid.uuid4())
        embed = await create_debug_embed(self.bot, ctx, tracking_uuid=tracking_uuid, message=msg)
        await self.bot.send_debug(embed=embed)
        await message.edit(content=f"已呼叫, 追蹤碼: `{tracking_uuid}`")

    @commands.is_owner()
    @commands.group(hidden=True)
    async def admin(self, ctx: Context):
        """
        Admin commands
        """
        if ctx.invoked_subcommand is None:
            return

    @admin.command(aliases=["r"])
    async def reply(self, ctx: Context, channel_id: int, *, msg: str):
        await self.bot.get_channel(channel_id).send(msg)

    @admin.command()
    async def activity(self, ctx: Context, *, text: str):
        """
        Change bot's activity
        """
        await self.bot.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                type=self.config.get(["activity", "type"]),
                name=f"{self.bot.config.get(['activity','prefix'])}{text}",
            ),
        )
        await self.bot.send_debug(embed=utils.notice_embed(f"Activity has been changed", text, ctx.author))
        await ctx.send(":white_check_mark: Sucess")

    @admin.command(aliases=["uc"])
    async def usage(self, ctx: Context):
        """
        Show command usage counts
        """
        counts = self.bot.counter.as_list()

        count_str = "```autohotkey\n"
        for i, j in counts:
            temp = f"{i}: {j}\n"
            if len(count_str) + len(temp) >= 2000:
                await ctx.send(count_str + "```")
                count_str = "```autohotkey\n"
            count_str += temp

        await ctx.send(count_str + "```")

    @admin.command()
    async def reload(self, ctx: Context, cog: str):
        """
        Reload cog
        """
        try:
            self.bot.reload_extension(cog)
            await ctx.send(":white_check_mark: Sucess")
        except Exception as e:
            await self.bot.send_debug(embed=utils.error_embed(f"Failed when reloading cog: {cog}", str(e), ctx.author))

    @admin.command()
    async def load(self, ctx: Context, cog: str):
        """
        Load cog
        """
        try:
            self.bot.load_extension(cog)
            await ctx.send(":white_check_mark: Sucess")
        except Exception as e:
            await self.bot.send_debug(embed=utils.error_embed(f"Failed when loading cog: {cog}", str(e), ctx.author))

    @admin.command()
    async def unload(self, ctx: Context, cog: str):
        """
        Unload cog
        """
        try:
            self.bot.unload_extension(cog)
            await ctx.send(":white_check_mark: Sucess")
        except Exception as e:
            await self.bot.send_debug(embed=utils.error_embed(f"Failed when unloading cog: {cog}", str(e), ctx.author))

    @admin.command()
    async def stop(self, ctx: Context):
        """
        Stop the bot :(
        """
        await self.bot.send_debug(embed=utils.notice_embed(f"Bot has been stopped", author=ctx.author))
        await ctx.send(":thumbsup: Bye~")
        await self.bot.close()

    @admin.command()
    async def exec(self, ctx: Context, *, command: str):
        """
        Execute command
        """
        self.logger.info(f"Execute: {command}")
        if command.startswith("await "):
            exe = await eval(command[6:])
        else:
            print(command)
            exe = eval(command)
        self.logger.info(f"Execute result: {exe}")

    @admin.command()
    async def clean_cache(self, ctx: Context, id: int = None):
        """
        Clear specific id or all state caches.
        """
        self.bot.stateManger.clean_cache(id)
        await ctx.send(":white_check_mark: Sucess")


def setup(bot):
    bot.add_cog(Admin(bot))
