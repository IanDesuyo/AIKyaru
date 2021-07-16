from main import AIKyaru
import utils
from typing import Union
from discord.ext import commands
from discord.ext.commands import Context
from discord_slash import cog_ext, SlashContext
import time
from cogs.common.gacha import Gacha
from cogs.common.sta import Sta


class Common(commands.Cog):
    def __init__(self, bot: AIKyaru):
        self.bot = bot

    def create_footer_links(self):
        links = [
            {"title": "幫助頁面", "url": "https://iandesuyo.notion.site/AI-v3-baec83903f764b7f95d0186f105190ee"},
            {
                "title": "邀請AI キャル",
                "url": f"https://discordapp.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=applications.commands%20bot",
            },
            {"title": "Discord群組", "url": "https://discord.gg/cwFc4qh"},
            {"title": "巴哈姆特哈拉版文章", "url": "https://forum.gamer.com.tw/Co.php?bsn=30861&sn=165061"},
            {"title": "Github", "url": "https://github.com/IanDesuyo/AIKyaru"},
        ]
        return " | ".join(["[{title}]({url})".format(**i) for i in links])

    #
    # Help
    #
    @commands.command(name="help", brief="幫助頁面", description="顯示幫助訊息", aliases=["幫助"])
    async def cmd_help(self, ctx: Context):
        await self._help(ctx)

    @cog_ext.cog_slash(
        name="help",
        description="顯示幫助訊息",
    )
    async def cog_help(self, ctx: SlashContext):
        await self._help(ctx)

    async def _help(self, ctx: Union[Context, SlashContext]):
        embed = utils.create_embed(
            title=self.bot.config.get(["helpTitle"]),
            description=f"指令前綴為`{self.bot.config.get(['prefix'])}`, 也可以標註我<@{self.bot.user.id}>喔~",
            author={"name": "幫助", "icon_url": f"{self.bot.config.get(['AssetsURL'])}/logo.png"},
            footer={"text": "©2021 AIキャル | 資料均取自互聯網,商標權等屬原提供者(Cygames, So-net Taiwan)"},
        )

        embed.add_field(
            name="\u200b",
            value=self.create_footer_links(),
            inline=False,
        )
        await ctx.send(embed=embed)

    #
    # Ping
    #
    @commands.command(name="ping", brief="Ping", description="Pong!")
    async def cmd_ping(self, ctx: Context):
        await self._ping(ctx)

    async def _ping(self, ctx: Union[Context, SlashContext]):
        before = time.monotonic()
        message = await ctx.send("Pong!")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"Pong!  `{int(ping)}ms`")

    #
    # Status
    #
    @commands.command(name="status", brief="機器人狀態", description="查看機器人狀態")
    async def cmd_status(self, ctx: Context):
        await self._status(ctx)

    @cog_ext.cog_slash(
        name="status",
        description="查看機器人狀態",
    )
    async def cog_status(self, ctx: SlashContext):
        await self._status(ctx)

    async def _status(self, ctx: Union[Context, SlashContext]):
        embed = utils.create_embed(
            description="Developed by [Ian#5898](https://ian.randosoru.me)",
            color=0x1BAED8,
            author={"name": "機器人狀態", "icon_url": f"{self.bot.config.get(['AssetsURL'])}/logo.png"},
            footer={"text": "©2021 AIキャル | 資料均取自互聯網,商標權等屬原提供者(Cygames, So-net Taiwan)"},
            thumbnail=f"{self.bot.config.get(['AssetsURL'])}/character_unit/106061.webp",
        )
        embed.add_field(name="所在伺服器數", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Gateway延遲", value=round(self.bot.latency, 2), inline=True)
        chance = " | 三星加倍中!" if self.bot.gameData.tw.rarity3_double else ""
        embed.add_field(
            name="模擬抽卡Pickup",
            value=" ".join([f"<:4:{i['id']}>" for i in [*self.bot.config.gacha_emojis["Pickup"]]]) + chance,
            inline=True,
        )
        embed.add_field(name="機器人版本", value=self.bot.__version__, inline=True)
        embed.add_field(name="台版資料庫版本", value=self.bot.config.game_data_version.tw["TruthVersion"], inline=True)
        embed.add_field(name="日版資料庫版本", value=self.bot.config.game_data_version.jp["TruthVersion"], inline=True)
        embed.add_field(name="資料庫更新時間", value=self.bot.config.game_data_version.updateTime, inline=True)
        embed.add_field(name="Rank推薦更新時間", value=self.bot.config.rank_data["source"]["updateTime"], inline=True)
        embed.add_field(
            name="\u200b",
            value=self.create_footer_links(),
            inline=False,
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Common(bot))
    bot.add_cog(Gacha(bot))
    bot.add_cog(Sta(bot))
