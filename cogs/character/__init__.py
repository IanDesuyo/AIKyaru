from typing import Union
from discord_slash.context import ComponentContext
from discord_slash.model import ButtonStyle
from cogs.character.embeds import Embeds
from main import AIKyaru
from utils import Unit
from utils.custom_id import pref_custom_id, un_pref_custom_id
from discord.ext import commands
from discord.ext.commands import Context
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import create_button, create_actionrow
from copy import deepcopy

type_buttons = create_actionrow(
    *[
        create_button(
            style=ButtonStyle.green,
            label="簡介",
            emoji={"name": "info", "id": 850732950600679464},
        ),
        create_button(
            style=ButtonStyle.gray,
            label="專武",
            emoji={"name": "ue", "id": 850732950642884608},
        ),
        create_button(
            style=ButtonStyle.blue,
            label="技能",
            emoji={"name": "skill", "id": 850732950847881226},
        ),
        create_button(
            style=ButtonStyle.gray,
            label="攻擊",
            emoji={"name": "icon_skill_attack", "id": 605337612835749908},
        ),
        create_button(
            style=ButtonStyle.red,
            label="RANK推薦",
            emoji={"name": "rank", "id": 850732950525575178},
        ),
    ]
)


class Character(commands.Cog):
    def __init__(self, bot: AIKyaru):
        self.bot = bot
        self.embedMaker = Embeds(bot)

    @commands.command(name="info", brief="角色資訊", description="查詢角色資訊", aliases=["i"], usage="<角色關鍵字>")
    async def cmd_info(self, ctx: Context, *, keyword: str):
        await self._init_embed(ctx, keyword, 1)

    @commands.command(name="ue", brief="角色專武", description="查詢角色專屬武器", usage="<角色關鍵字>")
    async def cmd_ue(self, ctx: Context, *, keyword: str):
        await self._init_embed(ctx, keyword, 2)

    @commands.command(name="skill", brief="角色技能", description="查詢角色技能", usage="<角色關鍵字>")
    async def cmd_skill(self, ctx: Context, *, keyword: str):
        await self._init_embed(ctx, keyword, 3)

    @commands.command(name="attack", brief="角色攻擊模式", description="查詢角色攻擊模式", aliases=["atk"], usage="<角色關鍵字>")
    async def cmd_attack(self, ctx: Context, *, keyword: str):
        await self._init_embed(ctx, keyword, 4)

    @commands.command(name="rank", brief="RANK推薦", description="查詢RANK推薦", usage="<角色關鍵字>")
    async def cmd_rank(self, ctx: Context, *, keyword: str):
        await self._init_embed(ctx, keyword, 5)

    @cog_ext.cog_slash(
        name="character",
        description="查詢角色資訊",
        options=[create_option(name="角色", description="可以是角色名稱或關鍵字", option_type=3, required=True)],
        connector={"角色": "keyword"},
    )
    async def cog_menu(self, ctx: SlashContext, keyword: str):
        type = await ctx.state.get_user(keys=["config", "character_default_type"]) or 1

        await self._init_embed(ctx, keyword, type)

    @cog_ext.cog_component()
    async def pref_character(self, ctx: ComponentContext):
        await self._handle_button(ctx)

    async def _init_embed(self, ctx: Union[Context, SlashContext], keyword: str, type: int):
        unit = self.bot.config.get_character(keyword)
        if not unit:
            return await ctx.send(f"找不到跟`{keyword}`有關的角色...")

        await ctx.send(**self.create_embed(unit, type))

    async def _handle_button(self, ctx: ComponentContext):
        # i = unit_id, t = type
        data = un_pref_custom_id(custom_id="character", data=ctx.custom_id)
        unit = self.bot.config.get_character_by_id(data["i"])

        await ctx.edit_origin(**self.create_embed(unit, data["t"]))

    def create_embed(self, unit: Unit, type: int):
        if type == 1:
            embed = self.embedMaker.profile(unit)
        elif type == 2:
            embed = self.embedMaker.unique_equipment(unit)
        elif type == 3:
            embed = self.embedMaker.skill(unit)
        elif type == 4:
            embed = self.embedMaker.atk_pattern(unit)
        elif type == 5:
            embed = self.embedMaker.rank(unit)

        # set button
        buttons = deepcopy(type_buttons)
        buttons["components"][type - 1]["disabled"] = True

        for i, j in enumerate(buttons["components"]):
            # i = unit_id, t = type
            j["custom_id"] = pref_custom_id(custom_id="character", data={"i": unit.id, "t": i + 1})

        return {"embed": embed, "components": [buttons]}


def setup(bot):
    bot.add_cog(Character(bot))
