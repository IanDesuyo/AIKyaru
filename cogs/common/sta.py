from main import AIKyaru
import utils
import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from datetime import datetime, timedelta
from typing import Optional, Union


class Sta(commands.Cog):
    def __init__(self, bot: AIKyaru):
        self.bot = bot

    @commands.command(name="sta", brief="體力計算機", aliases=["s", "體力計算"], usage="<目前體力(預設為0)> <主角等級(預設為台版上限)>")
    async def cmd_sta(self, ctx: Context, sta: int = 0, lv: Optional[int] = None):
        await self._sta(ctx, sta, lv)

    @cog_ext.cog_slash(
        name="sta",
        description="體力計算機",
        options=[
            create_option(name="當前體力", description="當前的體力, 預設為0", option_type=4, required=False),
            create_option(
                name="主角等級",
                description="主角等級, 預設為台版上限",
                option_type=4,
                required=False,
            ),
        ],
        connector={"當前體力": "sta", "主角等級": "lv"},
    )
    async def cog_sta(self, ctx: SlashContext, sta: int = 0, lv: int = None):
        await self._sta(ctx, sta, lv)

    async def _sta(self, ctx: Union[Context, SlashContext], sta: int = 0, lv: int = None):
        if not lv:
            lv = self.bot.gameData.tw.max_lv
        elif lv > self.bot.gameData.jp.max_lv:
            return await ctx.send(f"目前最高等級是{self.bot.gameData.jp.max_lv}, 你突破限制了嗎?")
        elif lv < 25:
            return await ctx.send("不支援主角等級低於25 :(")

        #  calculate max stamina
        if lv >= 27:
            max_sta = 58 + lv
        else:
            max_sta = 85 - (26 - lv) * 5
        if sta > max_sta:
            return await ctx.send(f"目前體力不能大於最大體力(`{max_sta}`)...")

        # calculate full time
        full_time = datetime.now() + timedelta(minutes=(max_sta - sta) * 5)
        full_time = full_time.strftime("%m/%d %H:%M")

        embed = utils.create_embed(
            author={"name": "體力計算", "icon_url": f"{self.bot.config.get(['AssetsURL'])}/item/93001.webp"}
        )
        embed.add_field(name="主角等級", value=lv, inline=True)
        embed.add_field(name="目前體力", value=sta, inline=True)
        embed.add_field(name="最大體力", value=max_sta, inline=True)
        embed.add_field(name="體力全滿時間", value=full_time, inline=True)

        await ctx.send(embed=embed)
