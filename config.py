import logging
import asyncio
import os
import json
from utils import download, GameDataVersion, Unit, FetchRank
from datetime import datetime
from discord.ext.commands import Bot
import re


class BotConfig:
    """
    Bot config
    """

    def __init__(self):
        """
        Load config from `./config.json` and download all required data.

        Raises:
            FileNotFoundError: Cound not find `./config.json`
        """
        self.logger = logging.getLogger("AIKyaru.config")
        self.gacha_emojis = {}

        if os.path.exists("./config.json"):
            with open("./config.json") as f:
                self._config = json.load(f)
        else:
            raise FileNotFoundError("./config.json")

        asyncio.get_event_loop().run_until_complete(self.update())

    async def update(self, reload_config=False):
        if reload_config:
            with open("./config.json") as f:
                self._config = json.load(f)
        self.logger.info("Downloading character keywords...")
        self.characters_keyword = await download.GSheet(**self.get(["keywordGSheet"]))
        self.logger.info(f"Done, characters: {len(self.characters_keyword)}.")

        self.logger.info("Downloading recommended ranks...")
        fr = FetchRank(self.characters_keyword, self.get(["RankData", "emonight"]), self.get(["RankData", "nonplume"]))
        self.rank_data = await fr.run()
        self.logger.info(f"Done, characters: {len(self.rank_data)-1}.")  # -1 for remove source data

        # check missing characters
        keyword_ids = list(self.characters_keyword.keys())
        rank_ids = list(self.rank_data.keys())
        rank_ids.remove("source")
        for i in rank_ids:
            keyword_ids.remove(int(i))

        if keyword_ids:
            self.logger.warning(f"Missing recommended ranks for {', '.join([str(i) for i in keyword_ids])}.")

        self.logger.info("Checking gameDB version...")
        await self.update_gameDB()
        self.logger.info("Done.")

    async def update_gameDB(self):
        lastVersion = {"jp": None, "tw": None}
        updated = False
        if os.path.exists("./gameDB/version.json"):
            with open("./gameDB/version.json") as f:
                lastVersion = json.load(f)
        self.logger.info(f"Last version: {lastVersion}")

        try:
            jp_ver = await download.json_(self.get(["RediveJP_DB"])[1])
            if lastVersion["jp"] != jp_ver:
                self.logger.info(f"Downloading RediveJP database ({jp_ver})...")
                await download.gameDB(self.get(["RediveJP_DB"])[0], "redive_jp.db")
                lastVersion["jp"] = jp_ver
                updated = True
        except:
            self.logger.warning("Download failed.")

        try:
            tw_ver = await download.json_(self.get(["RediveTW_DB"])[1])
            if lastVersion["tw"] != tw_ver:
                self.logger.info(f"Downloading RediveTW database ({tw_ver})...")
                await download.gameDB(self.get(["RediveTW_DB"])[0], "redive_tw.db")
                lastVersion["tw"] = tw_ver
                updated = True
        except:
            self.logger.warning("Download failed.")

        if updated:
            with open("./gameDB/version.json", "w+") as f:
                json.dump(lastVersion, f)
            self.logger.info(f"Newest version: {lastVersion}")

        self.game_data_version = GameDataVersion(
            lastVersion["jp"], lastVersion["tw"], datetime.now().strftime("%y/%m/%d %H:%M")
        )

    async def update_gacha_emojis(self, bot: Bot):
        self.logger.info("Fetching gacha emojis...")
        pickup_units = bot.gameData.tw.featured_gacha["unit_ids"]
        pickup_emojis = []
        pickup_ids = []
        for rarity in range(1, 4):
            rarity_emojis = []

            for i in self.get(["EmojiServers", rarity]):
                guild = await bot.fetch_guild(i)
                emojis = await guild.fetch_emojis()
                self.logger.debug(f"Found {len(emojis)} emojis at {i}")
                for emoji in emojis:
                    if int(emoji.name) in pickup_units:
                        pickup_emojis.append({"name": int(emoji.name), "id": emoji.id})
                        pickup_ids.append(int(emoji.name))
                    else:
                        rarity_emojis.append({"name": int(emoji.name), "id": emoji.id})

            self.gacha_emojis[rarity] = rarity_emojis

        for i in self.get(["EmojiServers", "Pickup"]):
            guild = await bot.fetch_guild(i)
            emojis = await guild.fetch_emojis()
            self.logger.debug(f"Found {len(emojis)} emojis at {i}")

            for emoji in emojis:
                if int(emoji.name) in pickup_units and int(emoji.name) not in pickup_ids:
                    pickup_emojis.append({"name": int(emoji.name), "id": emoji.id})

        if len(pickup_emojis) == 0:
            pickup_emojis.append({"name": 0000, "id": 852602645419130910})

        self.gacha_emojis["Pickup"] = pickup_emojis
        self.logger.info(f"Done, gacha emojis: {', '.join([f'{i}: {len(j)}' for i,j in self.gacha_emojis.items()])}")

    def get(self, keys: list = []):
        if not keys:
            return self._config

        x = self._config
        for i in keys:
            x = x.get(str(i))
            if not x:
                return None
        return x

    def get_character(self, keyword: str):
        """
        Find character by keyword

        Args:
            keyword (str): character keyword.

        Returns:
            :class:`Unit` if character can be found.
        """
        if len(keyword) > 20:
            return
        keyword = keyword.upper()
        for i, j in self.characters_keyword.items():
            if re.match(j["keyword"], keyword):
                return Unit(id=i, keyword=j["keyword"], name=j["display_name"], color=int(j["color"], 16))

        self.logger.debug(f"Cound not find the character matching {keyword}")

    def get_character_by_id(self, unit_id: int):
        """
        Find character by id.

        Args:
            unit_id (int): 4 code id.

        Returns:
            :class:`Unit` if character can be found.
        """
        unit = self.characters_keyword.get(unit_id)
        if unit:
            return Unit(id=unit_id, keyword=unit["keyword"], name=unit["display_name"], color=int(unit["color"], 16))

        self.logger.debug(f"Cound not get character by id {unit_id}")
