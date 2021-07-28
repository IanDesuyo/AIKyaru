from main import AIKyaru
import discord
from discord.ext import commands
from discord.ext.commands import Context
import re
from utils import damage_converter
import utils


class Cbre(commands.Cog):
    def __init__(self, bot: AIKyaru):
        self.bot = bot
        self.damage2regex = re.compile(r"(\d+[kKwW\d])(\((\d\d)\)|)")

    @commands.command(brief="補償計算機", aliases=["補償計算"], usage="<目標血量> <第一刀傷害> <第二刀傷害(剩餘秒數)>")
    async def cbre(self, ctx: Context, hp: damage_converter, damage1: damage_converter, damage2="10000"):
        try:
            damage2out = self.damage2regex.search(damage2)
            damage2 = damage_converter(damage2out.group(1))
            damage2time = int(damage2out.group(3)) if damage2out.group(3) else 0
            if hp == 0 or damage1 == 0 or damage2 == 0:
                return await ctx.send("血量和傷害不可為0")
        except:
            raise commands.BadArgument

        if (damage1 + damage2) < hp:
            return await ctx.send("兩刀還殺不掉王啊...")
        if hp < damage1:
            return await ctx.send("一刀就能殺掉了...")
        retime = 90 - (hp - damage1) / (damage2 / (90 - damage2time)) + 20
        retime = 90 if retime > 90 else retime
        if retime == 20:
            return await ctx.send("可能殺不死喔, 靠暴擊吧")
        redmg = round((damage2 / 90) * retime / 10000, 1)

        embed = utils.create_embed(
            author={"name": "補償計算", "icon_url": f"{self.bot.config.get(['AssetsURL'])}/item/99002.webp"},
            footer={"text": "出刀打王有賺有賠, 此資料僅供參考"},
        )

        embed.add_field(name="目標血量", value=f"{int(hp/10000)}萬", inline=True)
        embed.add_field(name="第一刀傷害", value=f"{int(damage1/10000)}萬", inline=True)
        embed.add_field(name="第二刀傷害", value=f"{int(damage2/10000)}萬", inline=True)
        embed.add_field(name="第二刀補償時間", value=f"{retime}秒", inline=True)
        embed.add_field(name="理想補償傷害", value=f"{redmg}萬", inline=True)

        await ctx.send(embed=embed)
