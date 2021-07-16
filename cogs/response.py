import discord
from discord.ext import commands
import random
import re

class Response(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if re.match(rf"^<@(!|){self.bot.user.id}>$", message.content):
            return await message.channel.send("幹..幹嘛啦...別亂叫我")
        if re.match(rf"^<@(!|){self.bot.user.id}>", message.content):
            text = message.content.lower()
            if re.match(r".*覺得呢(\?|)$", text):
                return await message.channel.send(
                    random.choice(
                        ["我..我怎麼知道啦~", "自己決定好嗎?", "隨便啦", "我覺得可以", "我覺得不行", "好像還可以", "不行", "可以", "好", "可以不要問我嗎...",]
                    )
                )
            elif re.match(r".*(可以|能).*(嗎|ㄇ)(\?|)$", text):
                return await message.channel.send(random.choice(["可以", "不行", "不可以"]))
            elif re.match(r".*是.*(嗎|ㄇ)(\?|)$", text):
                return await message.channel.send(random.choice(["是", "不是", "應該是吧?", "好像是"]))
            elif re.match(r".*(接|換)頭.*$", text):
                return await message.channel.send("能不能不要什麼都P個我的頭")
            elif re.match(r".*(道|ㄅ)(歉|欠).*$", text):
                return await message.channel.send(random.choice(["對不起", "對ㄅ起", "?", "不要啊"]))
            elif "可可蘿" in text:
                return await message.channel.send("可蘿仔")
            elif "凱留醬" in text:
                return await message.channel.send("怎樣啦!")
            elif "佩可" in text:
                return await message.channel.send("才..才不喜歡呢")
            elif re.match(r".*對不起(ue|優依|優衣).*$/i", text):
                return await message.channel.send("你才對不起UE")
            elif "考" in text:
                return await message.channel.send(random.choice(["蛤?", "考三小"]))
            elif "關起來" in text or "945" in text:
                return await message.channel.send(random.choice(["蛤?", "嗯?"]))
            elif "喵" in text:
                return await message.channel.send(random.choice(["喵..喵喵?", "喵..喵喵? 幹嘛啦~", "喵?", "?"]))
            elif "貓咪" in text or "喵咪" in text:
                return await message.channel.send(random.choice(["可愛", "可愛 <3"]))
            elif "婆" in text:
                return await message.channel.send(random.choice(["誰..誰是你婆啦!", "別睡了, 快醒來", "醒醒好嗎?"]))
            elif re.match(r".*喜歡(你|妳).*$", text):
                return await message.channel.send(random.choice(["你...在說什麼...啦...", "那個...不要亂說話啦...真是的"]))
            elif "結婚" in text:
                return await message.channel.send(random.choice(["別睡了, 快醒來", "醒醒好嗎?"]))
            elif "摸" in text:
                return await message.channel.send(random.choice(["你..別亂摸啊!", "誰..誰會喜歡被你摸啊?"]))
            elif "舔" in text:
                return await message.channel.send("你..別亂舔啊!")
            elif "臭鼬" in text:
                return await message.channel.send(random.choice(["你才臭鼬", "我看你是欠揍"]))
            elif "ちぇる" in text:
                return await message.channel.send(
                    random.choice(["ち...ちぇる? ちぇらりば、ちぇりり?", "ち..ちぇる? 你再說什麼啊...", "ちぇろっば、ちぇぽられ、ちぇろらろ",])
                )
            elif "切嚕" in text:
                return await message.channel.send(
                    random.choice(["切嚕～♪", "切..切嚕?", "切..切嚕? 你在說什麼啊...", "切嚕切嚕、切切嚕啪、切嚕嚕嚕嚕"])
                )
            elif "喂" in text:
                return await message.channel.send(random.choice(["怎樣啦", "幹嘛", "蛤"]))
            elif "吃蟲" in text:
                return await message.channel.send("我不要吃蟲啦!")
            elif "天氣怎樣" in text:
                return await message.channel.send(random.choice(["你不會自己Google嗎?", "自己去Google啦!"]))
            elif "吃什麼" in text:
                return await message.channel.send("去問佩可啦!")
            elif "沒錢" in text or "手頭很緊" in text:
                return await message.channel.send("這個我也幫不了你")
            elif "運勢如何" in text:
                return await message.channel.send("我怎麼知道")
            elif "小小甜心" in text:
                return await message.channel.send("你想表達什麼?")
            else:
                return await message.channel.send("?")


def setup(bot):
    bot.add_cog(Response(bot))
