import logging
from main import AIKyaru
import utils
import re
from utils import Unit


skill_emojis = {
    1: "<:0:605337612835749908>",
    1001: "<:1:605337612865241098>",
    1002: "<:2:605337613616021514>",
    2001: "<:1:863769653678440479>",
    2002: "<:2:863769653662842932>",
    2003: "<:3:863769653528363029>",
}


class Embeds:
    def __init__(self, bot: AIKyaru):
        self.bot = bot
        self.logger = logging.getLogger("AIKyaru.Character")

    def rank(self, unit: Unit):
        data = self.bot.config.rank_data.get(unit.id)
        if not data:
            embed = utils.create_embed(
                title="此角色尚無Rank推薦",
                description=f"**資料最後更新時間: {self.bot.config.rank_data['source']['updateTime']}**",
                color=unit.color,
                author={
                    "name": f"RANK推薦　{unit.name}",
                    "icon_url": f"{self.bot.config.get(['AssetsURL'])}/equipment/102312.webp",
                },
                thumbnail=f"{self.bot.config.get(['AssetsURL'])}/character_unit/{unit.id}31.webp",
            )

        else:
            # fmt: off
            embed = utils.create_embed(
                title=f"本次推薦\nE夢: {data['emonight']['preferRank']} / {data['emonight']['preferRarity']}\n"
                    + f"無羽: {data['nonplume']['preferRank']} / {data['nonplume']['preferRarity']}星",
                description=f"**資料最後更新時間: {self.bot.config.rank_data['source']['updateTime']}**",
                color=unit.color,
                author={"name": f"RANK推薦　{unit.name}", "icon_url": f"{self.bot.config.get(['AssetsURL'])}/equipment/102312.webp"},
                footer={"text": f"RANK為主觀想法, 結果僅供參考　資料來源: 無羽 / E夢 / 蘭德索爾圖書館"},
                thumbnail=f"{self.bot.config.get(['AssetsURL'])}/character_unit/{unit.id}31.webp",
            )
            embed.add_field(name="PVP (E夢/無羽)", value=f"{data['emonight']['pvp']} / {data['nonplume']['pvp']}", inline=True)
            embed.add_field(name="戰隊戰 (E夢/無羽)", value=f"{data['emonight']['cb']} / {data['nonplume']['cb']}", inline=True)
            embed.add_field(name="HP", value=data["diff"]["hp"], inline=True)
            embed.add_field(name="物攻 / 魔攻", value=f"{data['diff']['atk']} / {data['diff']['magic_str']}", inline=True)
            embed.add_field(name="物防 / 魔防", value=f"{data['diff']['def']} / {data['diff']['magic_def']}", inline=True)
            embed.add_field(name="物暴 / 魔暴", value=f"{data['diff']['physical_critical']} / {data['diff']['magic_critical']}", inline=True)
            embed.add_field(name="HP吸收 / 回復上升", value=f"{data['diff']['hp_steal']} / {data['diff']['hp_recovery_rate']}", inline=True)
            embed.add_field(name="HP自回 / TP自回", value=f"{data['diff']['wave_hp_recovery']} / {data['diff']['wave_energy_recovery']}", inline=True)
            embed.add_field(name="TP上升 / TP減輕", value=f"{data['diff']['energy_recovery_rate']} / {data['diff']['energy_reduce_rate']}", inline=True)
            embed.add_field(name="命中/ 迴避", value=f"{data['diff']['accuracy']} / {data['diff']['dodge']}", inline=True)
            embed.add_field(name="說明 By E夢", value=f"{data['emonight']['comment']}\n[詳細內容]({self.bot.config.rank_data['source']['emonight']})", inline=False)
            embed.add_field(name="說明 By 無羽", value=f"{data['nonplume']['comment']}\n[詳細內容]({self.bot.config.rank_data['source']['nonplume']})", inline=False)
            # fmt: on

        return embed

    def profile(self, unit: Unit):
        data = self.bot.gameData.tw.get_unit_profile(unit.id)
        if not data:
            data = self.bot.gameData.jp.get_unit_profile(unit.id)
        if not data:
            # should not trigger this
            self.logger.error(f"Could not find profile for {unit.name}({unit.id})")
            embed = utils.create_embed(
                title="此角色尚無角色簡介",
                color=unit.color,
                author={
                    "name": f"角色簡介　{unit.name}",
                    "icon_url": f"{self.bot.config.get(['AssetsURL'])}/item/31000.webp",
                },
                thumbnail=f"{self.bot.config.get(['AssetsURL'])}/character_unit/{unit.id}31.webp",
            )

        else:
            embed = utils.create_embed(
                title=unit.name,
                description=data["catch_copy"],
                color=unit.color,
                url=f"{self.bot.config.get(['PCRwiki'])}/{data['unit_name']}",
                author={
                    "name": f"角色簡介　{data['guild']}",
                    "icon_url": f"{self.bot.config.get(['AssetsURL'])}/item/31000.webp",
                },
                thumbnail=f"{self.bot.config.get(['AssetsURL'])}/character_unit/{unit.id}31.webp",
                footer={"text": re.sub(r"[\s\\n]", "", data["self_text"])},
            )
            embed.add_field(name="生日", value=f"{data['birth_month']}月{data['birth_day']}日", inline=True)
            embed.add_field(name="年齡", value=data["age"], inline=True)
            embed.add_field(name="身高", value=data["height"], inline=True)
            embed.add_field(name="體重", value=data["weight"], inline=True)
            embed.add_field(name="血型", value=data["blood_type"], inline=True)
            embed.add_field(name="種族", value=data["race"], inline=True)
            embed.add_field(name="喜好", value=data["favorite"], inline=True)
            embed.add_field(name="聲優", value=data["voice"], inline=True)
            embed.set_image(url=f"{self.bot.config.get(['AssetsURL'])}/character_card/{unit.id}31.webp")

        return embed

    def unique_equipment(self, unit: Unit):
        data = self.bot.gameData.tw.get_unit_unique_equipment(unit.id)
        if not data:
            data = self.bot.gameData.jp.get_unit_unique_equipment(unit.id)
        if not data:
            embed = utils.create_embed(
                title="此角色尚無專屬武器",
                color=unit.color,
                author={
                    "name": f"專用裝備　{unit.name}",
                    "icon_url": f"{self.bot.config.get(['AssetsURL'])}/item/99002.webp",
                },
                thumbnail=f"{self.bot.config.get(['AssetsURL'])}/character_unit/{unit.id}31.webp",
            )

        else:
            embed = utils.create_embed(
                title=data["equipment_name"],
                description=data["description"],
                color=unit.color,
                author={
                    "name": f"專用裝備　{unit.name}",
                    "icon_url": f"{self.bot.config.get(['AssetsURL'])}/item/99002.webp",
                },
                footer={"text": f"括號內為專用裝備滿等時(Lv.{self.bot.gameData.tw.max_enhance_lv})之數值"},
                thumbnail=f"{self.bot.config.get(['AssetsURL'])}/equipment/{data['equipment_id']}.webp",
            )

            for values in data["effects"]:
                embed.add_field(name=values[0], value=values[1], inline=True)

        return embed

    def skill(self, unit: Unit):
        data = self.bot.gameData.tw.get_unit_skill(unit.id)
        if not data:
            data = self.bot.gameData.jp.get_unit_skill(unit.id)
        if not data:
            # should not trigger this
            self.logger.error(f"Could not find skills for {unit.name}({unit.id})")
            embed = utils.create_embed(
                title="此角色尚無技能資訊",
                color=unit.color,
                author={
                    "name": f"技能資訊　{unit.name}",
                    "icon_url": f"{self.bot.config.get(['AssetsURL'])}/skill/2022.webp",
                },
                thumbnail=f"{self.bot.config.get(['AssetsURL'])}/character_unit/{unit.id}31.webp",
            )

        else:
            embed = utils.create_embed(
                color=unit.color,
                author={
                    "name": f"技能資訊　{unit.name}",
                    "icon_url": f"{self.bot.config.get(['AssetsURL'])}/skill/2022.webp",
                },
                thumbnail=f"{self.bot.config.get(['AssetsURL'])}/character_unit/{unit.id}31.webp",
            )

            for skill in data:
                embed.add_field(name=skill[0], value=skill[1], inline=False)

        return embed

    def atk_pattern(self, unit: Unit):
        data = self.bot.gameData.tw.get_unit_atk_pattern(unit.id)
        if not data:
            data = self.bot.gameData.jp.get_unit_atk_pattern(unit.id)
        if not data:
            # should not trigger this
            self.logger.error(f"Could not find attack pattern for {unit.name}({unit.id})")
            embed = utils.create_embed(
                title="此角色尚無攻擊模式",
                color=unit.color,
                author={
                    "name": f"攻擊模式　{unit.name}",
                    "icon_url": f"{self.bot.config.get(['AssetsURL'])}/equipment/101011.webp",
                },
                thumbnail=f"{self.bot.config.get(['AssetsURL'])}/character_unit/{unit.id}31.webp",
            )
        else:
            embed = utils.create_embed(
                color=unit.color,
                author={
                    "name": f"攻擊模式　{unit.name}",
                    "icon_url": f"{self.bot.config.get(['AssetsURL'])}/equipment/101011.webp",
                },
                thumbnail=f"{self.bot.config.get(['AssetsURL'])}/character_unit/{unit.id}31.webp",
            )

            for i, j in enumerate(data):
                pattern = (
                    "起始："
                    + ("→".join([skill_emojis[x] for x in j["start"]]))
                    + "\n循環："
                    + "→".join([skill_emojis[x] for x in j["loop"]])
                    + "↻"
                )
                embed.add_field(
                    name=f"模式{i+1}",
                    value=pattern,
                    inline=False,
                )

        return embed
