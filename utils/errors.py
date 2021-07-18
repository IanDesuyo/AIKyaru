from typing import Union
import discord
from discord import Embed
from discord.ext import commands
from discord.ext.commands import Bot, Context
from discord.ext.commands.errors import BotMissingPermissions
from discord_slash import SlashContext, ComponentContext
from datetime import datetime
from utils import how_to_use
import uuid
import utils
import traceback


class FormNotSet(Exception):
    pass


class FormNotFound(Exception):
    pass


class IncorrectFormId(Exception):
    pass


class IncorrectWeek(Exception):
    pass


class IncorrectBoss(Exception):
    pass


class IncorrectDamage(Exception):
    pass


class IncorrectComment(Exception):
    pass


class ReportNotFinish(Exception):
    pass


class RecordDeleted(Exception):
    pass


async def handle_error(bot: Bot, ctx: Union[Context, SlashContext, ComponentContext], error):
    if isinstance(ctx, ComponentContext):
        # don't send new message, edit the origin one.
        async def do_edit_origin(content: str = "", embed=None, components=None):
            await ctx.edit_origin(content=content, embed=embed, components=components)

        ctx.send = do_edit_origin

    if isinstance(error, (commands.CommandNotFound, commands.NotOwner, discord.Forbidden, discord.NotFound)):
        return
    if isinstance(error, (commands.BadArgument, commands.MissingRequiredArgument)):
        return await ctx.send(
            how_to_use(f"{bot.config.get(['prefix'])}{ctx.command.name} {getattr(ctx.command, 'usage','')}")
        )
    if isinstance(error, commands.CommandOnCooldown):
        return await ctx.send(f"等..等一下啦! 太快了... (`{int(error.retry_after)}s`)")
    if isinstance(error, commands.MissingPermissions):
        return await ctx.send(f"你沒有權限... 需要`{','.join(error.missing_perms)}`")
    if isinstance(error, BotMissingPermissions):
        return await ctx.send(f"我沒有權限... 需要`{','.join(error.missing_perms)}`")
    if isinstance(error, commands.NoPrivateMessage):
        return await ctx.send("此功能僅限群組使用")

    # clan errors

    if isinstance(error, FormNotSet):
        return await ctx.send("此群組還沒綁定報名表...")
    if isinstance(error, FormNotFound):
        return await ctx.send("找不到此報名表... 或許你打錯字了?")
    if isinstance(error, IncorrectFormId):
        return await ctx.send("你是不是打錯字了? 報名表ID應該要是32字的UUID")
    if isinstance(error, IncorrectWeek):
        return await ctx.send("周次要在1~200之內喔")
    if isinstance(error, IncorrectDamage):
        return await ctx.send("這什麼傷害? 要在1~40,000,000之內喔")
    if isinstance(error, IncorrectComment):
        return await ctx.send("備註太長啦! 要40字以內喔")
    if isinstance(error, ReportNotFinish):
        return await ctx.send("此功能僅限於傷害回報選擇`自訂`時可使用喔!")
    if isinstance(error, RecordDeleted):
        return await ctx.send("<:scared:605380139760615425> 紀錄消失了...", embed=None, components=None)

    tracking_uuid = str(uuid.uuid4())
    embed = await create_debug_embed(bot, ctx, tracking_uuid, error=error)

    await bot.send_debug(embed=embed)
    try:
        await ctx.send(f":rotating_light: 發生錯誤, 追蹤碼: `{tracking_uuid}`")
    except discord.Forbidden:
        pass

    bot.logger.error(f"ERROR: {tracking_uuid}")
    raise error


async def create_debug_embed(
    bot: Bot,
    ctx: Union[Context, SlashContext, ComponentContext],
    tracking_uuid: str,
    message: str = Embed.Empty,
    error: Exception = None,
):
    if error:
        description = str(error)
        if isinstance(ctx, Context):
            title = f"Context: {ctx.command}\n`{ctx.message.content}`"
            ts = ctx.message.created_at
        elif isinstance(ctx, SlashContext):
            title = f"SlashContext: {ctx.command}\n`{ctx.data}`"
            ts = ctx.created_at
        elif isinstance(ctx, ComponentContext):
            title = f"ComponentContext: {ctx.custom_id}\n`{ctx.data}`"
            ts = ctx.created_at
    else:
        title = None
        description = message
        ts = datetime.now()

    is_guild = getattr(ctx, "guild", None)
    author_state = await ctx.state.get_user()

    if is_guild:
        bot_permissions = ctx.channel.permissions_for(ctx.guild.me if ctx.guild is not None else ctx.bot.user)
        author_permissions = ctx.channel.permissions_for(ctx.author)
        guild_state = await ctx.state.get_guild()

    embed = utils.create_embed(
        title=title or "Call for help",
        description=description,
        color=0xE82E2E if error else "default",
        author={"name": "\U0001f6a8 ERROR Report" if error else "Debug Report"},
        footer={
            "text": f"Triggered by {ctx.author.name}#{ctx.author.discriminator}\n{tracking_uuid}",
            "icon_url": str(ctx.author.avatar_url),
        },
    )
    embed.timestamp = ts
    embed.add_field(name="Author", value=f"{ctx.author.name}#{ctx.author.discriminator}\n{ctx.author.id}")
    embed.add_field(name="Guild", value=is_guild and f"{ctx.guild.name}\n{ctx.guild.id}")
    embed.add_field(name="Channel", value=is_guild and f"{ctx.channel.name}\n{ctx.channel.id}")
    embed.add_field(name="Author State", value=author_state, inline=False)
    embed.add_field(name="Guild State", value=is_guild and guild_state, inline=False)
    embed.add_field(
        name="Bot Permissions",
        value=is_guild
        and f"[{bot_permissions.value}](https://discordapi.com/permissions.html#{bot_permissions.value})",
    )
    embed.add_field(
        name="Author Permissions",
        value=is_guild
        and f"[{author_permissions.value}](https://discordapi.com/permissions.html#{author_permissions.value})",
    )
    if error:
        try:
            raise error
        except:
            tb = traceback.format_exc(limit=2)
            if len(tb) <= 1000:
                embed.add_field(name="Traceback", value=f"```\n{tb}```", inline=False)
            else:
                embed.add_field(name="Traceback", value=f"```\n{str(error)}```", inline=False)

    return embed