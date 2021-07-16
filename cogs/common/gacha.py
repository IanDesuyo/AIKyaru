from main import AIKyaru
import utils
import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
import random
from typing import Optional, Union


class Gacha(commands.Cog):
    def __init__(self, bot: AIKyaru):
        self.bot = bot

    @commands.command(
        name="gacha", brief="抽卡模擬", description="一時抽卡一時爽, 一直抽卡一直爽", aliases=["抽卡", "抽", "r"], usage="<抽數(1~300)>"
    )
    async def cmd_status(self, ctx: Context, num: Optional[int] = 10):
        await self._gacha(ctx, num, 1)

    @cog_ext.cog_slash(
        name="gacha",
        description="一時抽卡一時爽, 一直抽卡一直爽",
        options=[
            create_option(name="次數", description="抽卡次數, 1~300抽", option_type=4, required=False),
            create_option(
                name="卡池",
                description="目標抽取卡池",
                option_type=4,
                required=False,
                choices=[create_choice(value=1, name="精選轉蛋"), create_choice(value=2, name="白金轉蛋")],
            ),
        ],
        connector={"次數": "count", "卡池": "pool"},
    )
    async def cog_gacha(
        self,
        ctx: SlashContext,
        count: int = 10,
        pool: int = 1,
    ):
        await self._gacha(ctx, count, pool)

    async def _gacha(self, ctx: Union[Context, SlashContext], num: int, pool: int):
        if num < 1:
            return await ctx.send("你是要抽幾次...")
        if num > 300:
            num = 300

        if isinstance(ctx.channel, discord.channel.DMChannel):
            sender = ctx.author.name
        else:
            sender = ctx.author.nick or ctx.author.name

        x = [random.uniform(0, 1) for i in range(num)]
        rarity3_double = 2 if (pool == 1 and self.bot.gameData.tw.rarity3_double) else 1
        megami = 0
        count = 0

        if num > 10:
            res = [0, 0, 0]
            pickup = [0 for i in self.bot.gameData.tw.featured_gacha["unit_ids"]]
            for i in x:
                count += 1
                if i <= 0.007 * rarity3_double:
                    megami += 50
                    pickup[random.randrange(len(pickup))] += 1
                elif i <= 0.025 * rarity3_double:
                    megami += 50
                    res[2] += 1
                elif i <= 0.18 or count % 10 == 0:
                    megami += 10
                    res[1] += 1
                else:
                    megami += 1
                    res[0] += 1
            msg = (
                f"經過了{num}抽的結果,\n{sender} 的石頭變成了{megami}個<:0:605373812619345931>\n"
                + " ".join(
                    [
                        f"<:4:{self.bot.config.gacha_emojis.get('Pickup')[i]['id']}> x{pickup[i]}"
                        for i in range(len(pickup))
                    ]
                )
                + f" + 保底x1\n"
                + f"<:3_star:607908043962712066> x{res[2]}\n"
                + f"<:2_star:607908043031838722> x{res[1]}\n"
                + f"<:1_star:607908043954323467> x{res[0]}"
            )
            return await ctx.send(msg)

        res = []
        pickup = 0
        for i in x:
            count += 1
            if i <= 0.007 * rarity3_double:
                res.append(f"<:4:{random.choice(self.bot.config.gacha_emojis.get('Pickup'))['id']}>")
                megami += 50
                pickup += 1
            elif i <= 0.025 * rarity3_double:
                res.append(f"<:3:{random.choice(self.bot.config.gacha_emojis.get(3))['id']}>")
                megami += 50
            elif i <= 0.18 or count == 9:
                res.append(f"<:2:{random.choice(self.bot.config.gacha_emojis.get(2))['id']}>")
                megami += 10
            else:
                res.append(f"<:1:{random.choice(self.bot.config.gacha_emojis.get(1))['id']}>")
                megami += 1

        msg = f"{sender} 的石頭變成了{megami}個<:0:605373812619345931>\n"
        if pickup > 0:
            msg += "**你抽到了這次的Pick UP!**\n"
        if megami == 19:
            msg += random.choice(["保..保底...", "非洲人484", "保底 ㄏㄏ", "石頭好好玩", "可憐哪"])
        elif megami > 200:
            msg += random.choice(["歐洲人4你", "騙人的吧...", "..."])
        elif megami > 100:
            msg += random.choice(["還不錯喔", "你好棒喔"])
        await ctx.send(msg)
        await ctx.send(" ".join(res[0:5]) + "\n" + " ".join(res[5:10]))
