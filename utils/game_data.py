import sqlite3
import re


class GameData:
    def __init__(self, db_path: str):
        self.con = sqlite3.connect(db_path)
        self.con.row_factory = self.dict_factory
        self.cur = self.con.cursor()
        self.analytics()

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def analytics(self):
        featured_gacha = self.get_featured_gacha_pickup()
        self.rarity3_double = featured_gacha["rarity3_double"] == 1
        self.featured_gacha = featured_gacha
        self.max_lv = self.get_max_lv()
        self.max_enhance_lv = self.get_max_enhance_lv()
        self.tower_schedule = self.get_tower_schedule()

    def get_featured_gacha_pickup(self) -> dict:
        """
        Returns:
            A dict with :str:`gacha_name`, :str:`description`, :str:`start_time`, :str:`end_time`, :list:`unit_ids` and :int:`rarity3_double`.
        """
        data = self.cur.execute(
            """
            SELECT a.gacha_name, a.description, a.start_time, a.end_time,
                (SELECT group_concat(b.unit_id, ',') FROM gacha_exchange_lineup b WHERE b.exchange_id = a.exchange_id) AS unit_ids,
                CASE a.rarity_odds WHEN 600000 THEN 1 ELSE 0 END rarity3_double
            FROM gacha_data a
            WHERE a.exchange_id != 0 AND a.gacha_times_limit10 != 1 AND (a.prizegacha_id != 0 OR a.gacha_bonus_id != 0) AND REPLACE(a.start_time, '/', '-') <= datetime('now', '+8 hours')
            ORDER BY a.start_time DESC LIMIT 1
            """,
        ).fetchone()
        data["unit_ids"] = [int(i[:4]) for i in data.get("unit_ids").split(",")]
        return data

    def get_max_lv(self) -> int:
        data = self.cur.execute("SELECT stat AS lv FROM sqlite_stat1 WHERE tbl = 'skill_cost'").fetchone()
        return int(data["lv"])

    def get_max_enhance_lv(self) -> int:
        data = self.cur.execute("SELECT MAX(enhance_level) AS lv FROM unique_equipment_enhance_data LIMIT 1").fetchone()
        return int(data["lv"])

    def get_tower_schedule(self) -> dict:
        """
        Returns:
            A dict with :int:`max_floor`, :int:`max_ex_floor`, :str:`start_time` and :str:`end_time`.
        """
        data = self.cur.execute(
            """
            SELECT MAX(a.max_floor_num) AS max_floor, MAX(a.tower_area_id) AS max_ex_floor, b.start_time, b.end_time
            FROM tower_area_data a, tower_schedule b 
            WHERE b.max_tower_area_id = a.tower_area_id
            """
        ).fetchone()
        return data

    def get_unit_profile(self, unit_id: int) -> dict:
        data = self.cur.execute("SELECT * FROM unit_profile WHERE unit_id = ? LIMIT 1", (unit_id * 100 + 1,)).fetchone()
        return data

    def get_unit_unique_equipment(self, unit_id: int):
        """
        Each effect will returned as a list, e.g. `["Effect", "default_value(max_value)"]`.

        Returns:
            A dict with :int:`equipment_id`, :str:`equipment_name`, :str:`description` and :list:`effects`.
        """
        data1 = self.cur.execute(
            "SELECT * FROM unique_equipment_data WHERE equipment_id = ? LIMIT 1", (f"13{unit_id-1000:03}1",)
        ).fetchone()

        if data1:
            data1_list = list(data1.values())
            effect_names = [
                "HP",
                "物理攻撃力",
                "魔法攻擊力",
                "物理防禦",
                "魔法防禦",
                "物理暴擊",
                "魔法暴擊",
                "HP自動回復",
                "TP自動回復",
                "迴避",
                "physical_penetrate",
                "magic_penetrate",
                "生命吸收",
                "回復量上升",
                "TP上升",
                "TP消耗減輕",
                "enable_donation",
                "命中",
            ]
            effects = []
            data2_list = list(
                self.cur.execute(
                    "SELECT * FROM unique_equipment_enhance_rate WHERE equipment_id = ? LIMIT 1",
                    (f"13{unit_id-1000:03}1",),
                )
                .fetchone()
                .values()
            )
            for i in range(8, 26):
                if int(data1_list[i]) != 0:
                    max_value = int(data1_list[i]) + 1
                    if i <= 23:
                        max_value = int(data1_list[i] + (data2_list[i - 4] * self.max_enhance_lv - 1)) + 1
                    effects.append([effect_names[i - 8], f"{data1_list[i]}({max_value})"])

            return {
                "equipment_id": data1["equipment_id"],
                "equipment_name": data1["equipment_name"],
                "description": data1["description"].replace("\\n", ""),
                "effects": effects,
            }

    def get_unit_skill(self, unit_id: int):
        """
        Each skill will returned as a list, e.g. `["Skill name", "Description", "Icon type", skill_id]`.

        Returns:
            A list sorted by skill_id.
        """
        data = self.cur.execute(
            # """
            # SELECT a.skill_id, a.name, a.icon_type, b.*
            # FROM skill_data a, skill_action b
            # WHERE a.skill_id LIKE '1158%' AND b.action_id IN (a.action_1, a.action_2, a.action_3, a.action_4, a.action_5, a.action_6, a.action_7)
            # """,
            "SELECT skill_id, name, description, icon_type FROM skill_data WHERE skill_id LIKE ? ORDER BY skill_id DESC",
            (f"{unit_id}%",),
        ).fetchall()
        skills = []
        s61 = False
        s62 = False
        for i in data:
            if str(i["skill_id"]).endswith("511"):
                skills.append([f"EX技能: {i['name']}", i["description"], i["icon_type"], 3])
            if str(i["skill_id"]).endswith("012"):
                skills.append([f"技能1: {i['name']}", i["description"], i["icon_type"], 1])
                s62 = True
            if str(i["skill_id"]).endswith("002") and not s62:
                skills.append([f"技能1: {i['name']}", i["description"], i["icon_type"], 1])
            if str(i["skill_id"]).endswith("003"):
                skills.append([f"技能2: {i['name']}", i["description"], i["icon_type"], 2])
            if str(i["skill_id"]).endswith("011"):
                skills.append([f"必殺技: {i['name']}", i["description"], i["icon_type"], 0])
                s61 = True
            if str(i["skill_id"]).endswith("001") and not s61:
                skills.append([f"必殺技: {i['name']}", i["description"], i["icon_type"], 0])
        skills.sort(key=lambda x: x[3])
        return skills

    def get_unit_atk_pattern(self, unit_id: int):
        """
                `1`, `100X` and `200Y` means normal attack, skill X and special skill Y.
        s
                Returns:
                    A list contains start and loop lists of all patterns.
        """
        data = self.cur.execute(
            "SELECT * FROM unit_attack_pattern WHERE unit_id = ? ORDER BY pattern_id", (unit_id * 100 + 1,)
        ).fetchall()
        if data:
            result = []
            for i in data:
                pattern = list(i.values())
                start = [x for x in pattern[4 : 3 + pattern[2]] if x != 0]
                loop = [x for x in pattern[3 + pattern[2] : 4 + pattern[3]] if x != 0]
                result.append({"start": start, "loop": loop})
            return result


class GameDataServer:
    """
    Contains :class:`GameData` for tw and jp.
    """

    def __init__(self, path: str = "./gameDB"):
        """
        Load `redive_{tw/jp}.db` from :str:`path`.
        """
        self.tw = GameData(f"{path}/redive_tw.db")
        self.jp = GameData(f"{path}/redive_jp.db")
