from copy import deepcopy
from datetime import datetime
from main import AIKyaru
import utils
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_button, create_actionrow
import random
from utils.custom_id import pref_custom_id
from cogs.clan.options import boss_buttons, week_buttons, damage_buttons, status_options

finish_messages = [":tada: 蘭德索爾又度過了平穩的一天"]


status_str = {
    1: "正式刀      ",
    2: "補償刀      ",
    3: "凱留刀      ",
    11: "戰鬥中      ",
    12: "等待中      ",
    13: "等待@mention",
    21: "完成(正式)  ",
    22: "完成(補償)  ",
    23: "暴死        ",
    24: "求救        ",
}

status_ids = list(status_str.keys())

status_pref = {
    1: " \u26AA ",
    2: " \U0001F7E4 ",
    3: " \U0001F7E3 ",
    11: " \U0001F7E0 ",
    12: " \U0001F535 ",
    13: " \U0001F535 ",
    21: "+\U0001F7E2 ",
    22: "+\U0001F7E2 ",
    23: "-\U0001F534 ",
    24: "-\U0001F534 ",
}

boss_str = {1: "一王", 2: "二王", 3: "三王", 4: "四王", 5: "五王"}


class Embeds:
    def __init__(self, bot: AIKyaru):
        self.bot = bot
        self.author = {
            "name": "戰隊管理協會",
            "icon_url": "https://guild.randosoru.me/static/images/icon/64x64.png",
            "url": "https://guild.randosoru.me",
        }

    def create_author(self, title: str):
        author = {
            "name": f"戰隊管理協會 | {title}",
            "icon_url": "https://guild.randosoru.me/static/images/icon/64x64.png",
            "url": "https://guild.randosoru.me",
        }
        return author

    def form_sucess(self, form: dict):
        embed = utils.create_embed(
            title=f":white_check_mark: 當前的報名表已設定為「{form['title']}」",
            color="default",
            author=self.author,
        )
        embed.add_field(name="月份", value=form["month"], inline=True)
        embed.add_field(name="報名表ID", value=form["id"], inline=False)

        components = create_actionrow(
            *[create_button(style=ButtonStyle.URL, label="點我前往", url=f"https://guild.randosoru.me/forms/{form['id']}")]
        )

        return embed, components

    def record_boss(self, records: list, form: dict, week: int, boss_data: dict):
        content = "```diff\n"
        total_damage = 0
        if len(records) == 0:
            content += "# 尚無紀錄"
        else:
            for i, j in enumerate(records):
                status = status_str[j["status"]]
                name = j["user"]["name"]
                comment = j["comment"]
                last_modified = datetime.fromtimestamp(j["last_modified"]).strftime("%m/%d %H:%M")
                if j["damage"]:
                    damage = f"DMG: {j['damage']:10,}"
                    total_damage += j["damage"]
                else:
                    damage = f"DMG:      未回報"

                record = status_pref[j["status"]]
                record += " | ".join([status, name]) + "\n  ├ "
                record += " | ".join(filter(None, [damage, comment])) + "\n"
                record += f"  {'└' if i == len(records)-1 else '├'} @ {last_modified}\n"
                content += record

        content += "```"

        damage_percent = int((total_damage / boss_data["hp"]) * 100)
        if damage_percent > 100:
            damage_percent = 100

        hpbar = (
            ("\U0001F7E5" * round((100 - damage_percent) / 10))
            + ("\u2B1C" * round(damage_percent / 10))
            + f" {100-damage_percent}% {boss_data['hp']-total_damage:,}/{boss_data['hp']:,}\n"
        )

        embed = utils.create_embed(
            title=f"{boss_data['name']} ({week}周{boss_data['boss']}王)",
            description=hpbar + content,
            thumbnail=boss_data["image"],
            url=f"https://guild.randosoru.me/forms/{form['id']}/week/{week}",
            author=self.create_author(form["title"]),
            footer={"text": f"{form['month']} | {form['id']} | 資料獲取時間"},
        )
        embed.timestamp = datetime.utcnow()

        components = self.create_record_buttons(form["id"], week, boss_data["boss"])
        return embed, components

    def create_record_buttons(self, form_id: str, week: int, boss: int):
        # i = form_id, w = week, b = boss
        buttons = deepcopy(boss_buttons)
        week_btns = deepcopy(week_buttons)
        buttons["components"][boss - 1]["disabled"] = True

        for i, j in enumerate(buttons["components"]):
            j["custom_id"] = pref_custom_id(custom_id="clan.records", data={"i": form_id, "w": week, "b": i + 1})

        if week == 1:
            week_btns["components"][0]["disabled"] = True
        else:
            week_btns["components"][0]["custom_id"] = pref_custom_id(
                custom_id="clan.records", data={"i": form_id, "w": week - 1, "b": 1}
            )

        if week == 200:
            week_btns["components"][1]["disabled"] = True
        else:
            week_btns["components"][1]["custom_id"] = pref_custom_id(
                custom_id="clan.records", data={"i": form_id, "w": week + 1, "b": 1}
            )

        return [buttons, week_btns]

    def new_report(self, form: dict, week: int, boss: int, boss_data: dict):
        embed = utils.create_embed(
            title=f"要在 {form['title']}\n創建一筆 {boss_data['name']} ({week}周{boss}王) 的記錄嗎?",
            description="請於下方選擇紀錄狀態",
            thumbnail=boss_data["image"],
            author=self.create_author(form["title"]),
            footer={"text": f"{form['month']} | {form['id']}"},
        )

        components = deepcopy(status_options)
        components["components"][0]["custom_id"] = pref_custom_id(
            custom_id="clan.report.new", data={"i": form["id"], "w": week, "b": boss}
        )

        return embed, components

    def record_created(self, form: dict, week: int, boss_data: dict, status: int, record_id: int):
        embed = utils.create_embed(
            title=f"已在 {form['title']}\n創建一筆 {boss_data['name']} ({week}周{boss_data['boss']}王) 的紀錄!",
            thumbnail=boss_data["image"],
            author=self.create_author(form["title"]),
            footer={"text": f"{form['month']} | {form['id']}"},
        )
        embed.add_field(name="狀態", value=status_str[status].strip(), inline=True)
        embed.add_field(name="紀錄編號", value=record_id, inline=True)

        components = self.create_record_update_buttons(form["id"], week, boss_data["boss"], status, record_id)

        return embed, components

    def record_updated(self, form: dict, week: int, boss_data: dict, status: int, record_id: int):
        embed = utils.create_embed(
            title=f"{week}周{boss_data['boss']}王({boss_data['name']}) 的紀錄已更新!",
            thumbnail=boss_data["image"],
            author=self.create_author(form["title"]),
            footer={"text": f"{form['month']} | {form['id']}"},
        )
        embed.add_field(name="狀態", value=status_str[status].strip(), inline=True)
        embed.add_field(name="紀錄編號", value=record_id, inline=True)

        components = self.create_record_update_buttons(form["id"], week, boss_data["boss"], status, record_id)

        return embed, components

    def create_record_update_buttons(self, form_id: str, week: int, boss: int, status: int, record_id: int):
        if status < 20:
            components = deepcopy(status_options)
            components["components"][0]["options"][status_ids.index(status)]["default"] = True
            components["components"][0]["custom_id"] = pref_custom_id(
                custom_id="clan.report.update", data={"i": form_id, "w": week, "b": boss, "r": record_id}
            )
            if status > 10:
                components["components"][0]["options"] = components["components"][0]["options"][3:]
        else:
            components = deepcopy(damage_buttons)
            for i in range(3):
                components["components"][i]["custom_id"] = pref_custom_id(
                    custom_id="clan.report.finish",
                    data={"i": form_id, "w": week, "b": boss, "c": i + 1, "s": status, "r": record_id},
                )

        return components

    def record_finish(self, form: dict, week: int, boss_data: dict, status: int, record: dict, user_data: dict):
        embed = utils.create_embed(
            title=f"{user_data['name']} 已完成出刀",
            description=random.choice(finish_messages),
            thumbnail=boss_data["image"],
            author=self.create_author(form["title"]),
            footer={"text": f"{form['month']} | {form['id']}"},
        )
        embed.add_field(name="周次/Boss", value=f"{boss_data['name']} {week}周{boss_data['boss']}王", inline=True)
        embed.add_field(name="狀態", value=status_str[status].strip(), inline=True)
        embed.add_field(name="傷害", value=f"{record['damage']:,}" if record["damage"] else "無", inline=True)
        embed.add_field(name="備註", value=record["comment"] or "無", inline=True)
        embed.add_field(
            name="最後更新時間", value=datetime.fromtimestamp(record["last_modified"]).strftime("%m/%d %H:%M:%S"), inline=True
        )
        embed.add_field(
            name="紀錄創建時間", value=datetime.fromtimestamp(record["created_at"]).strftime("%m/%d %H:%M:%S"), inline=True
        )
        embed.add_field(name="紀錄編號", value=record["id"], inline=True)

        return embed
