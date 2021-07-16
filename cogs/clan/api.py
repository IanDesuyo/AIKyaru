from datetime import datetime
import logging
from discord import User
from main import AIKyaru
from aiohttp import ClientSession, ClientTimeout
from expiringdict import ExpiringDict
from utils import errors
from copy import deepcopy
import re


class Api:
    def __init__(self, bot: AIKyaru):
        self.bot = bot
        self.logger = logging.getLogger("AIKyaru.ClanApi")
        self.apiUrl = self.bot.config.get(["GUILD_API_URL"])
        self.session = ClientSession(
            headers={
                "User-Agent": "AIKyaru v3",
                "x-token": self.bot.config.get(["GUILD_API_TOKEN"]),
            },
            timeout=ClientTimeout(total=10),
        )
        self.user_cache = ExpiringDict(max_len=1000, max_age_seconds=86400)  # cache user data for 1 day
        self.form_cache = ExpiringDict(max_len=1000, max_age_seconds=600)  # cache form data for 10 mins
        self.record_cache = ExpiringDict(
            max_len=100, max_age_seconds=10
        )  # cache records for 10 secs to prevent high api use

    
    def form_id_check(self, form_id: str):
        if not re.match(r"^[0-9a-fA-F]{32}$", form_id):
            raise errors.IncorrectFormId

    async def get_user(self, user: User):
        cached = self.user_cache.get(user.id)
        if cached:
            return cached

        async with self.session.get(
            f"{self.apiUrl}/bot/isRegister",
            params={"platform": 1, "user_id": user.id},
        ) as resp:
            data = await resp.json()

        self.logger.debug(f"isRegister {user.id}: {resp.status}")

        if resp.status == 404:
            async with self.session.post(
                f"{self.apiUrl}/bot/register",
                json={"platform": 1, "user_id": user.id, "avatar": str(user.avatar_url), "name": user.name},
            ) as resp:
                data = await resp.json()

                if resp.status == 400:
                    self.logger.error(f"register {user.id}: {data}")
                    raise ValueError("重複註冊")

            self.logger.debug(f"register {user.id}: {resp.status}")

        
        self.user_cache[user.id] = data
        return data

    async def get_form(self, form_id: str):
        cached = self.form_cache.get(form_id)
        if cached:
            return cached

        async with self.session.get(f"{self.apiUrl}/forms/{form_id}") as resp:
            data = await resp.json()

        self.logger.debug(f"get_form {form_id}: {resp.status}")
        if resp.status == 404:
            raise errors.FormNotFound(form_id)

        self.form_cache[form_id] = data
        return data

    async def create_form(self, user: User, title: str, month: int = None):
        if not month:
            month = datetime.now().strftime("%Y%m")

        user_data = await self.get_user(user)
        async with self.session.post(
            f"{self.apiUrl}/bot/forms/create",
            params={"user_id": user_data["id"]},
            json={"month": month, "title": title},
        ) as resp:
            data = await resp.json()
        
        self.logger.debug(f"create_form {title}: {resp.status}")
        return data

    async def get_record(self, form_id: str, week: int = None, boss: int = None):
        path = "/all"
        if week:
            path = f"/week/{week}"
        if boss:
            path += f"/boss/{boss}"

        cached = self.record_cache.get(path)
        if cached:
            return cached

        async with self.session.get(f"{self.apiUrl}/forms/{form_id}{path}") as resp:
            data = await resp.json()

        self.logger.debug(f"get_record /{form_id}/{week}/{boss}: {len(data)} records")
        self.record_cache[path] = data
        return data

    async def get_boss(self, form_id: str, week: int, boss: int):
        form = await self.get_form(form_id)
        boss_data = deepcopy(form["boss"][boss - 1])

        if week >= 45:
            stage = 5
        elif week >= 35:
            stage = 4
        elif week >= 11:
            stage = 3
        elif week >= 4:
            stage = 2
        else:
            stage = 1

        boss_data["hp"] = boss_data["hp"][stage - 1]

        return boss_data

    async def post_record(
        self,
        form_id: str,
        week: int,
        boss: int,
        status: int,
        user_id: str,
        damage: int = None,
        comment: str = None,
        record_id: int = None,
        month: int = None,
    ):
        async with self.session.post(
            f"{self.apiUrl}/bot/forms/{form_id}/week/{week}/boss/{boss}",
            params={"user_id": user_id},
            json={"id": record_id, "status": status, "damage": damage, "comment": comment, "month": month},
        ) as resp:
            data = await resp.json()
            
            if resp.status == 404:
                raise errors.RecordDeleted

        self.logger.debug(f"post_record /{form_id}/{week}/{boss}: {resp.status}")
        return data