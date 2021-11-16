from datetime import datetime
from aiohttp import ClientSession, ClientTimeout
import re
import json
import logging

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
}


class FetchRank:
    def __init__(self, keywords: dict, emonight_sheet: dict, nonplume_sheet: dict):
        self.logger = logging.getLogger("AIKyaru.FetchRank")
        self.session = ClientSession(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
            },
            timeout=ClientTimeout(total=10),
        )
        self.keywords = keywords
        self.result = {}
        self.source = {}
        self.emonight_sheet = emonight_sheet
        self.nonplume_sheet = nonplume_sheet

    async def run(self):
        await self.emonight()
        await self.nonplume()
        await self.session.close()
        self.check_data()
        self.source["updateTime"] = datetime.now().strftime("%m/%d %H:%M")
        return {**self.result, "source": self.source}

    async def emonight(self):
        async with self.session.get(
            f"https://docs.google.com/spreadsheets/u/0/d/{self.emonight_sheet['key']}/gviz/tq?gid={self.emonight_sheet['gid']}&tqx=out:json&tq={self.emonight_sheet['sql']}"
        ) as resp:
            data = re.search(r"(\{.*\})", await resp.text())
            data = json.loads(data.group(1))

        cols = self.column_check_emonight([i["label"].strip() for i in data["table"]["cols"]])
        result = {}
        unique_check = []
        for row in data["table"]["rows"]:
            row = row["c"]
            names = re.split(r"\n| ", row[cols["name"]]["v"].strip())
            name = names[0]
            if len(names) > 1 and names[1].startswith("("):
                name += names[1]

            id, name = self.find_id(name)
            if not id:
                continue
            elif id in unique_check:
                self.logger.error(f"Non-unique {name} ({id})")
                continue
            else:
                unique_check.append(id)

            # fmt: off
            row_result = {}
            row_diff = {}
            row_result["name"] = name

            emonight = {}
            emonight["preferRank"] = row[cols["preferRank"]]["v"].replace("\n", " ")
            emonight["preferRarity"] = row[cols["preferRarity"]]["v"].replace("\n", " ") if cols.get("preferRarity") and row[cols["preferRarity"]] else "-"
            emonight["comment"] = row[cols["comment"]]["v"].replace("\n", "") if row[cols["comment"]] else "-"
            emonight["pvp"] = row[cols["pvp"]]["v"] if row[cols["pvp"]] else "天下無雙"
            emonight["cb"] = row[cols["cb"]]["v"] if row[cols["cb"]] else "天下無雙"
            row_result["emonight"] = emonight

            row_result["attackRange"] = row[cols["attackRange"]]["v"] if row[cols["attackRange"]] else "-"
            row_diff["hp"] = self.get_value(row[cols["hp"]])
            row_diff["atk"] = self.get_value(row[cols["atk"]])
            row_diff["magic_str"] = self.get_value(row[cols["magic_str"]])
            row_diff["def"] = self.get_value(row[cols["def"]])
            row_diff["magic_def"] = self.get_value(row[cols["magic_def"]])
            row_diff["physical_critical"] = self.get_value(row[cols["physical_critical"]])
            row_diff["magic_critical"] = self.get_value(row[cols["magic_critical"]])
            row_diff["accuracy"] = self.get_value(row[cols["accuracy"]])
            row_diff["dodge"] = self.get_value(row[cols["dodge"]])
            row_diff["hp_steal"] = self.get_value(row[cols["hp_steal"]])
            row_diff["energy_reduce_rate"] = self.get_value(row[cols["energy_reduce_rate"]])
            row_diff["energy_recovery_rate"] = self.get_value(row[cols["energy_recovery_rate"]])
            row_diff["wave_energy_recovery"] = self.get_value(row[cols["wave_energy_recovery"]])
            row_diff["wave_hp_recovery"] = self.get_value(row[cols["wave_hp_recovery"]])
            row_diff["hp_recovery_rate"] = self.get_value(row[cols["hp_recovery_rate"]])
            # fmt: on

            row_result["diff"] = row_diff
            result[id] = row_result

        self.result = result
        self.source["emonight"] = f"https://docs.google.com/spreadsheets/d/{self.emonight_sheet['key']}/htmlview"

    async def nonplume(self):
        async with self.session.get(
            f"https://docs.google.com/spreadsheets/u/0/d/{self.nonplume_sheet['key']}/gviz/tq?gid={self.nonplume_sheet['gid']}&tqx=out:json&tq={self.nonplume_sheet['sql']}"
        ) as resp:
            data = re.search(r"(\{.*\})", await resp.text())
            data = json.loads(data.group(1))

        cols = self.column_check_nonplume([i["label"].strip() for i in data["table"]["cols"]])
        unique_check = []
        for row in data["table"]["rows"]:
            row = row["c"]
            if not row[cols["name"]] or row[cols["name"]]["v"] == "名稱":
                continue
            names = re.split(r"\n| ", row[cols["name"]]["v"].strip())
            name = names[0]
            if len(names) > 1 and names[1].startswith("("):
                name += names[1]

            id, name = self.find_id(name)
            if not id:
                continue
            elif id in unique_check:
                self.logger.error(f"Non-unique {name} ({id})")
                continue
            else:
                unique_check.append(id)

            if self.result[id]["name"] != name:
                self.logger.error(f"Error {name} ({id})")

            nonplume = {}
            try:
                nonplume["pvp"] = row[cols["pvp"]]["v"]
                nonplume["cb"] = row[cols["cb"]]["v"]
                nonplume["preferRank"] = row[cols["preferRank"]]["v"] if row[cols["preferRank"]] else "-"
                nonplume["preferRarity"] = row[cols["preferRarity"]]["v"]
                nonplume["comment"] = row[cols["comment"]]["v"]
                self.result[id]["nonplume"] = nonplume
            except:
                pass

        self.source["nonplume"] = f"https://docs.google.com/spreadsheets/d/{self.nonplume_sheet['key']}/htmlview"

    def get_value(self, i):
        if i:
            if i["v"] != None:
                return i["v"]
        return "-"

    def find_id(self, name):
        for i, j in self.keywords.items():
            if re.match(j["keyword"], name):
                return i, j["display_name"]
        self.logger.warning(f"Character not found: {name}")
        return None, None

    # fmt: off
    def column_check_emonight(self, cols):
        correct_columns = {}
        for i, j in enumerate(cols):
            if j == "角色名": correct_columns["name"] = i
            elif j == "本次推薦": correct_columns["preferRank"] = i
            elif j == "星專建議": correct_columns["preferRarity"] = i
            elif j == "升Rank短評": correct_columns["comment"] = i
            elif j == "PVP評價": correct_columns["pvp"] = i
            elif j == "聯盟戰評價": correct_columns["cb"] = i
            elif j == "攻擊距離": correct_columns["attackRange"] = i
            elif j == "HP": correct_columns["hp"] = i
            elif j == "物攻": correct_columns["atk"] = i
            elif j == "魔攻": correct_columns["magic_str"] = i
            elif j == "物防": correct_columns["def"] = i
            elif j == "魔防": correct_columns["magic_def"] = i
            elif j == "物暴": correct_columns["physical_critical"] = i
            elif j == "魔暴": correct_columns["magic_critical"] = i
            elif j == "命中": correct_columns["accuracy"] = i
            elif j == "迴避": correct_columns["dodge"] = i
            elif j == "HP吸收": correct_columns["hp_steal"] = i
            elif j == "TP減輕": correct_columns["energy_reduce_rate"] = i
            elif j == "TP上升": correct_columns["energy_recovery_rate"] = i
            elif j == "TP自回": correct_columns["wave_energy_recovery"] = i
            elif j == "HP自回": correct_columns["wave_hp_recovery"] = i
            elif j == "回復上升": correct_columns["hp_recovery_rate"] = i

        if len(correct_columns.keys()) != 22:
            self.logger.warning(f"column_check_emonight | {correct_columns}")

        return correct_columns

    def column_check_nonplume(self, cols):
        correct_columns = {}
        for i, j in enumerate(cols):
            if j == "名稱": correct_columns["name"] = i
            elif j == "使用率 戰隊": correct_columns["cb"] = i
            elif j == "競技": correct_columns["pvp"] = i
            elif "RANK" in j: correct_columns["preferRank"] = i
            elif "星級" in j: correct_columns["preferRarity"] = i
            elif j == "個人說明欄": correct_columns["comment"] = i

        if len(correct_columns.keys()) != 6:
            self.logger.warning(f"column_check_nonplume | {correct_columns}")
        
        return correct_columns

    # fmt: on

    def check_data(self):
        for i, j in self.result.items():
            if not "nonplume" in j:
                self.result[i]["nonplume"] = {
                    "pvp": "-",
                    "cb": "-",
                    "preferRank": "-",
                    "preferRarity": "-",
                    "comment": "無",
                }
