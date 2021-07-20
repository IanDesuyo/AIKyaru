import logging
from discord_slash.context import ComponentContext
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_components import create_actionrow, create_button
from main import AIKyaru
from utils.custom_id import pref_custom_id, un_pref_custom_id
from typing import Union
from discord.ext import commands
from discord.ext.commands import Context
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
import asyncio
import secrets
from aiohttp import ClientSession, ClientTimeout
from utils import create_profile_embed, errors
import re
from copy import deepcopy
from datetime import datetime

verify_buttons = create_actionrow(*[create_button(style=ButtonStyle.green, label="點我驗證")])


class ProfileCard(commands.Cog):
    def __init__(self, bot: AIKyaru):
        self.bot = bot
        self.logger = logging.getLogger("AIKyaru.ProfileCard")
        self.apiUrl = self.bot.config.get(["GAME_API_URL"])
        self.session = ClientSession(
            headers={"User-Agent": "AIKyaru v3", "x-token": self.bot.config.get(["GAME_API_TOKEN"])},
            timeout=ClientTimeout(total=10),
        )

    def cog_unload(self):
        asyncio.get_event_loop().run_until_complete(self.session.close())

    #
    # Functions
    #
    async def get_profile(self, server: int, uid: int, cache: bool = True):
        async with self.session.get(
            f"{self.apiUrl}/profile",
            params={"server": server, "uid": uid, "cache": "true" if cache else "false"},
        ) as resp:
            data = await resp.json()

        self.logger.info(f"get_profile /{server}/{uid}: {resp.status}")

        if resp.status == 404:
            raise errors.ProfileNotFound
        if resp.status == 500:
            raise errors.GameApiError

        return data

    #
    # Commands
    #
    @commands.group(name="profile", brief="個人檔案", description="查看個人檔案")
    async def cmd_profile(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            await self._profile(ctx)

    @cog_ext.cog_slash(
        name="profile",
        description="查看個人檔案",
    )
    async def cog_profile(self, ctx: SlashContext):
        await self._profile(ctx)

    async def _profile(self, ctx: Union[Context, SlashContext]):
        linked_uid = await ctx.state.get_user(keys=["linked_uid"])
        if not linked_uid:
            return await ctx.send("尚未綁定")

        await ctx.defer()
        data = await self.get_profile(**linked_uid)
        await ctx.send(embed=create_profile_embed(data))

    @cmd_profile.command(name="bind", brief="綁定遊戲ID", description="將Discord帳號與遊戲ID綁定", usage="<伺服器(1~4)> <遊戲ID(9位數)>")
    async def cmd_bind(self, ctx: Context, server: int, uid: int):
        if server < 1 and server > 4:
            return ctx.send("伺服器錯誤, 請輸入1~4")
        await self._bind(ctx, server, uid)

    @cog_ext.cog_slash(
        name="profile_bind",
        description="綁定遊戲內個人檔案",
        options=[
            create_option(
                name="伺服器",
                description="伺服器編號(1~4)",
                option_type=4,
                choices=[
                    create_choice(value=1, name="美食殿堂"),
                    create_choice(value=2, name="真步真步王國"),
                    create_choice(value=3, name="破曉之星"),
                    create_choice(value=4, name="小小甜心"),
                    # Currently unsupported
                    # create_choice(value=0, name="日版"),
                ],
                required=True,
            ),
            create_option(name="遊戲id", description="9位數ID", option_type=4, required=True),
        ],
        connector={"伺服器": "server", "遊戲id": "uid"},
    )
    async def cog_bind(self, ctx: SlashContext, server: int, uid: int):
        await self._bind(ctx, server, uid)

    async def _bind(self, ctx: Union[Context, SlashContext], server: int, uid: int):
        if not re.match(r"^\d{9}$", str(uid)):
            return await ctx.send("遊戲ID錯誤", hidden=True)

        verify_code = secrets.token_hex(3).upper()
        buttons = deepcopy(verify_buttons)
        # s = server, i = uid, v = verify_code, t = created_at
        buttons["components"][0]["custom_id"] = pref_custom_id(
            custom_id="user.link_uid",
            data={"s": server, "i": uid, "v": verify_code, "t": int(datetime.now().timestamp())},
        )
        await ctx.send(f"請在遊戲內個人簡介內加入以下代碼 `{verify_code}` , 有效時間2分鐘.", components=[buttons], hidden=True)

    @cog_ext.cog_component(components="pref_user.link_uid")
    async def pref_user_link_uid(self, ctx: ComponentContext):
        # s = server, i = uid, v = verify_code, t = created_at
        data = un_pref_custom_id(custom_id="user.link_uid", data=ctx.custom_id)

        if datetime.now().timestamp() > data["t"] + 120:
            return await ctx.edit_origin(content="此驗證已過期", components=None)

        await ctx.defer(edit_origin=True)
        profile_data = await self.get_profile(data["s"], data["i"], False)

        if str(data["v"]) in profile_data["user_info"]["user_comment"]:
            profile_data["user_info"]["user_comment"] = profile_data["user_info"]["user_comment"].replace(
                str(data["v"]), ""
            )
            await ctx.state.set_user({"linked_uid": {"server": data["s"], "uid": data["i"]}})
            return await ctx.edit_origin(
                content=":white_check_mark: 驗證成功", embed=create_profile_embed(profile_data), components=None
            )

        await ctx.edit_origin(content="驗證失敗", components=None)


def setup(bot):
    bot.add_cog(ProfileCard(bot))
