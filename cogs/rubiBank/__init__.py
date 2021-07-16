from main import AIKyaru
from datetime import datetime
from typing import Union
from discord.ext import commands
from discord.ext.commands import Context
from discord_slash import cog_ext, SlashContext


class RubiBank(commands.Cog):
    def __init__(self, bot: AIKyaru):
        self.bot = bot

    @commands.group(name="rubi", hidden=True)
    async def cmd_rubi(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await self._balance(ctx)

    @cmd_rubi.command(name="sign", brief="簽到", description="每日簽到")
    async def cmd_sign(self, ctx: Context):
        await self._sign(ctx)

    @cog_ext.cog_subcommand(
        base="rubi",
        name="sign",
        description="每日簽到",
    )
    async def cog_sign(self, ctx: SlashContext):
        await self._sign(ctx)

    async def _sign(self, ctx: Union[Context, SlashContext]):
        bank = await ctx.state.get_user(keys=["bank"]) or {"rubi": 0, "signDate": ""}
        today = datetime.now().strftime("%y%m%d")

        if bank.get("signDate") == today:
            return await ctx.send(f"你今天已經簽到過了...")

        bank["rubi"] += 100
        bank["signDate"] = today
        await ctx.state.set_user({"bank": bank})

        return await ctx.send(f"簽到成功, 你現在有 {bank['rubi']}盧幣")

    @cmd_rubi.command(name="balance", brief="查看盧幣", description="查看你有多少盧幣")
    async def cmd_balance(self, ctx: Context):
        await self._balance(ctx)

    @cog_ext.cog_subcommand(
        base="rubi",
        name="balance",
        description="查看你有多少盧幣",
    )
    async def cog_balance(self, ctx: SlashContext):
        await self._balance(ctx)

    async def _balance(self, ctx: Union[Context, SlashContext]):
        bank = await ctx.state.get_user(keys=["bank"]) or {"rubi": 0}
        return await ctx.send(f"你現在有 {bank['rubi']}盧幣")


def setup(bot):
    bot.add_cog(RubiBank(bot))
