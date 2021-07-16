from utils import errors
from main import AIKyaru
from discord import Message
from discord.ext import commands
import re

chinese2num = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "壹": 1, "貳": 2, "參": 3, "肆": 4, "伍": 5}


class ClanResponse(commands.Cog):
    def __init__(self, bot: AIKyaru):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.guild and str(self.bot.user.id) in message.content:  # mention and guild filter
            reg_1 = re.search(r"([1-5一二三四五])王死(了|ㄌ|囉)$", message.content)
            if reg_1:
                try:
                    boss = int(reg_1.group(1))
                except ValueError:
                    boss = chinese2num[reg_1.group(1)]
                guild_state = await self.bot.stateManger.get_guild(message.guild.id)
                clan = guild_state.get("clan")
                if not clan:
                    raise errors.FormNotSet

                week = clan.get("week")
                boss += 1
                if boss == 6:
                    boss = 1
                    week += 1

                await self.bot.stateManger.set_guild(message.guild.id, {"clan.boss": boss, "clan.week": week})
                await message.channel.send(f":thumbsup: 現在為{week}周{boss}王")


def setup(bot):
    bot.add_cog(ClanResponse(bot))
