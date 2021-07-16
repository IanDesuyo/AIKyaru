import asyncio
from typing import Union
from discord.ext.commands import Context, NoPrivateMessage
from discord_slash import SlashContext, ComponentContext
from motor.motor_asyncio import AsyncIOMotorClient
from expiringdict import ExpiringDict
import logging


class StateManger:
    """
    A simple state manger to get or set the state of user (or guild).
    """

    def __init__(self, mongo_url: str, database: str = "AIKyaru"):
        """
        The `user` and `guild` collections should be created before init.

        Args:
            mongo_url (str): A full mongodb URI.
            database (str): Your database name.
        """
        self.logger = logging.getLogger("AIKyaru.StateManger")
        client = AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=5000)
        self.db = client[database]
        self.user = self.db["user"]
        self.guild = self.db["guild"]
        self.cache = ExpiringDict(
            max_len=1000, max_age_seconds=300
        )  # Discord utilizes snoflakes, so ids should always be unique.

    def clean_cache(self, id: int = None):
        """
        Clear specific id or all caches.

        Args:
            id (int, optional): User or guild id. Defaults to None.
        """
        if id:
            self.logger.debug(f"{id} cache cleared")
            self.cache.pop(id)
        else:
            self.logger.info("All caches have been cleared")
            self.cache.clear()

    async def get_user(self, id: int):
        cached = self.cache.get(id)
        if cached:
            self.logger.debug(f"get_user {id} cached")
            return cached

        self.logger.debug(f"get_user {id}")
        res = await self.user.find_one({"id": id}) or {}
        self.cache[id] = res
        return res

    async def set_user(self, id: int, data: dict = {}, unset: bool = False):
        if unset:
            self.logger.info(f"unset_user {id} | {data}")
            await self.user.update_one({"id": id}, {"$unset": data}, upsert=True)
        else:
            self.logger.info(f"set_user {id} | {data}")
            await self.user.update_one({"id": id}, {"$set": data}, upsert=True)

        self.cache.pop(id)

    async def get_guild(self, id: int):
        cached = self.cache.get(id)
        if cached:
            self.logger.debug(f"get_guild {id} cached")
            return cached

        self.logger.debug(f"get_guild {id}")
        res = await self.guild.find_one({"id": id}) or {}
        self.cache[id] = res
        return res

    async def set_guild(self, id: int, data: dict = {}, unset: bool = False):
        if unset:
            self.logger.info(f"unset_guild {id} | {data}")
            await self.guild.update_one({"id": id}, {"$unset": data}, upsert=True)
        else:
            self.logger.info(f"set_guild {id} | {data}")
            await self.guild.update_one({"id": id}, {"$set": data}, upsert=True)

        self.cache.pop(id)


class State:
    """
    A class that will be set to ctx.state.
    """

    def __init__(self, sm: StateManger, ctx: Union[Context, SlashContext, ComponentContext]):
        self.sm = sm
        self.user_id = getattr(ctx, "author_id", ctx.author.id)
        self.guild_id = getattr(ctx, "guild_id", getattr(ctx.guild, "id", None))

    async def get_user(self, keys: list = []):
        data = await self.sm.get_user(self.user_id)
        for i in keys:
            data = data.get(i)
            if data == None:
                break

        return data

    async def set_user(self, data: dict = {}, unset: bool = False):
        await self.sm.set_user(self.user_id, data, unset)

    async def get_guild(self, keys: list = []):
        if not self.guild_id:
            raise NoPrivateMessage()

        data = await self.sm.get_guild(self.guild_id)
        for i in keys:
            data = data.get(i)
            if data == None:
                break
        return data

    async def set_guild(self, data: dict = {}, unset: bool = False):
        if not self.guild_id:
            raise NoPrivateMessage()

        await self.sm.set_guild(self.guild_id, data, unset)
