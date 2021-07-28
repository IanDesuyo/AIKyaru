import logging
from discord.ext.commands.cooldowns import BucketType
from discord_slash.context import ComponentContext
from cogs.character.embeds import Embeds
from main import AIKyaru
from utils import errors
from utils.custom_id import un_pref_custom_id
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from cogs.clan.api import Api
from cogs.clan.embeds import Embeds
from cogs.clan.options import boss_choices
from cogs.clan.cbre import Cbre
from discord_slash.utils.manage_commands import create_option
from cogs.clan.response import ClanResponse
import asyncio


class Clan(commands.Cog):
    def __init__(self, bot: AIKyaru):
        self.bot = bot
        self.logger = logging.getLogger("AIKyaru.Clan")
        self.api = Api(bot)
        self.embedMaker = Embeds(bot)

    def cog_unload(self):
        asyncio.get_event_loop().run_until_complete(self.api.session.close())

    async def get_form_state(self, ctx) -> dict:
        clan = await ctx.state.get_guild(keys=["clan"]) or {}
        if not clan.get("form_id"):
            raise errors.FormNotSet

        return clan

    async def set_form_state(self, ctx: SlashContext, form: dict):
        await ctx.state.set_guild({"clan": {"form_id": form["id"], "month": form["month"], "week": 1, "boss": 1}})

    @cog_ext.cog_subcommand(
        base="clan",
        name="set",
        description="戰隊系統相關設定",
        options=[
            create_option(name="報名表id", description="設定與此群組綁定的報名表", option_type=3, required=False),
            create_option(name="week", description="設定當前周次", option_type=4, required=False),
            create_option(name="boss", description="設定當前Boss", option_type=4, choices=boss_choices, required=False),
        ],
        connector={"報名表id": "form_id"},
    )
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def cog_clan_set(self, ctx: SlashContext, form_id: str = None, week: int = None, boss: int = None):
        if not form_id and not week and not boss:
            return await ctx.send("你想要我設定什麼...")

        content = []
        embed = None
        components = []

        if form_id:
            form_id = form_id.lower()
            self.api.form_id_check(form_id)

            await ctx.defer()
            form = await self.api.get_form(form_id)
            await self.set_form_state(ctx, form)

            embed, x = self.embedMaker.form_sucess(form)
            components.append(x)

        # check if form_id is set
        if not form_id and not await ctx.state.get_guild(keys=["clan", "form_id"]):
            raise errors.FormNotSet

        if week:
            if week < 0 or week > 200:
                raise errors.IncorrectWeek

            await ctx.state.set_guild({"clan.week": week})
            content.append(f":white_check_mark: 當前周次已設為`{week}`")

            await ctx.state.set_guild({"clan.boss": boss})
            content.append(f":white_check_mark: 當前Boss已設為`{boss}`")

        await ctx.send(content="\n".join(content) or None, embed=embed, components=components)

    @cog_ext.cog_subcommand(
        base="clan",
        name="create",
        description="創建新的報名表",
        options=[create_option(name="名稱", description="報名表名稱", option_type=3, required=False)],
        connector={"名稱": "form_name"},
    )
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1, 86400, BucketType.guild)
    async def cog_clan_create(self, ctx: SlashContext, form_name: str = None):
        if not form_name:
            form_name = ctx.guild.name

        await ctx.defer()

        form = await self.api.create_form(ctx.author, form_name)
        await self.set_form_state(ctx, form)

        embed, components = self.embedMaker.form_sucess(form)
        await ctx.send(embed=embed, components=[components])

    @cog_ext.cog_subcommand(
        base="clan",
        name="records",
        description="查看報名列表",
        options=[
            create_option(name="week", description="指定周次, 預設為群組當前周次", option_type=4, required=False),
            create_option(
                name="boss", description="指定Boss, 預設為群組當前Boss", option_type=4, choices=boss_choices, required=False
            ),
        ],
    )
    @commands.guild_only()
    async def cog_records(self, ctx: SlashContext, week: int = None, boss: int = None):
        if week and (week < 0 or week > 200):
            raise errors.IncorrectWeek

        form_state = await self.get_form_state(ctx)
        form_id = form_state.get("form_id")
        week = week or form_state.get("week", 1)
        boss = boss or form_state.get("boss", 1)

        form = await self.api.get_form(form_id)
        boss_data = await self.api.get_boss(form_id, week, boss)
        records = await self.api.get_record(form_id, week, boss)

        embed, components = self.embedMaker.record_boss(records, form, week, boss_data)

        await ctx.send(embed=embed, components=components, hidden=True)

    @cog_ext.cog_component(components="pref_clan.records")
    async def pref_clan_record(self, ctx: ComponentContext):
        # i = form_id, w = week, b = boss
        data = un_pref_custom_id(custom_id="clan.records", data=ctx.custom_id)

        form = await self.api.get_form(data["i"])
        boss_data = await self.api.get_boss(data["i"], data["w"], data["b"])
        records = await self.api.get_record(data["i"], data["w"], data["b"])

        embed, components = self.embedMaker.record_boss(records, form, data["w"], boss_data)

        await ctx.edit_origin(embed=embed, components=components)

    @cog_ext.cog_subcommand(
        base="clan",
        name="report",
        description="回報紀錄",
        options=[
            create_option(name="week", description="指定周次, 預設為群組當前周次", option_type=4, required=False),
            create_option(
                name="boss", description="指定Boss, 預設為群組當前Boss", option_type=4, choices=boss_choices, required=False
            ),
        ],
    )
    @commands.guild_only()
    async def cog_report(self, ctx: SlashContext, week: int = None, boss: int = None):
        if week and (week < 0 or week > 200):
            raise errors.IncorrectWeek

        form_state = await self.get_form_state(ctx)
        form_id = form_state.get("form_id")
        week = week or form_state.get("week", 1)
        boss = boss or form_state.get("boss", 1)

        form = await self.api.get_form(form_id)
        boss_data = await self.api.get_boss(form_id, week, boss)

        embed, components = self.embedMaker.new_report(form, week, boss, boss_data)

        await ctx.send(embed=embed, components=[components], hidden=True)

    @cog_ext.cog_component(components="pref_clan.report.new")
    async def pref_clan_report_new(self, ctx: ComponentContext):
        # i = form_id, w = week, b = boss, s = status
        data = un_pref_custom_id(custom_id="clan.report.new", data=ctx.custom_id)
        status = int(ctx.selected_options[0])

        form = await self.api.get_form(data["i"])
        boss_data = await self.api.get_boss(data["i"], data["w"], data["b"])
        user_data = await self.api.get_user(ctx.author)

        record = await self.api.post_record(
            data["i"], data["w"], data["b"], status, user_data["id"], month=form["month"]
        )

        embed, components = self.embedMaker.record_created(form, data["w"], boss_data, status, record["id"])

        await ctx.edit_origin(content=None, embed=embed, components=[components])

    @cog_ext.cog_component(components="pref_clan.report.update")
    async def pref_clan_report_update(self, ctx: ComponentContext):
        # i = form_id, w = week, b = boss, s = status, r = record_id
        data = un_pref_custom_id(custom_id="clan.report.update", data=ctx.custom_id)
        status = int(ctx.selected_options[0])

        form = await self.api.get_form(data["i"])
        boss_data = await self.api.get_boss(data["i"], data["w"], data["b"])
        user_data = await self.api.get_user(ctx.author)

        record = await self.api.post_record(
            data["i"], data["w"], data["b"], status, user_data["id"], record_id=data["r"], month=form["month"]
        )

        embed, components = self.embedMaker.record_updated(form, data["w"], boss_data, status, data["r"])

        await ctx.edit_origin(content=None, embed=embed, components=[components])

    @cog_ext.cog_component(components="pref_clan.report.finish")
    async def pref_clan_report_finish(self, ctx: ComponentContext):
        # i = form_id, w = week, b = boss, s = status, r = record_id, c = finish_type
        data = un_pref_custom_id(custom_id="clan.report.finish", data=ctx.custom_id)

        form = await self.api.get_form(data["i"])
        boss_data = await self.api.get_boss(data["i"], data["w"], data["b"])
        user_data = await self.api.get_user(ctx.author)

        if data["c"] == 3:  # custom damage and comment
            await ctx.state.set_user({"clan.finish_record": data})
            return await ctx.edit_origin(content=f"請使用`/clan finish`來完成回報!", embed=None, components=None)

        record = await self.api.post_record(
            data["i"],
            data["w"],
            data["b"],
            data["s"],
            user_data["id"],
            record_id=data["r"],
            month=form["month"],
            damage=boss_data["hp"],
            comment="物理一刀" if data["c"] == 1 else "魔法一刀",
        )

        embed = self.embedMaker.record_finish(form, data["w"], boss_data, data["s"], record, user_data)

        await ctx.edit_origin(content=":white_check_mark: 已完成出刀", embed=None, components=None)
        await ctx.send(embed=embed)

    @cog_ext.cog_subcommand(
        base="clan",
        name="finish",
        description="完成自訂回報",
        options=[
            create_option(name="傷害", description="對Boss造成的實際傷害, 不得大於40,000,000", option_type=4, required=False),
            create_option(name="備註", description="紀錄的備註, 上限40字", option_type=3, required=False),
        ],
        connector={"傷害": "damage", "備註": "comment"},
    )
    async def cog_finish(self, ctx: SlashContext, damage: int = None, comment: str = None):
        # i = form_id, w = week, b = boss, s = status, r = record_id, c = finish_type
        data = await ctx.state.get_user(keys=["clan", "finish_record"])
        if not data:
            raise errors.ReportNotFinish

        if damage and (damage < 0 or damage > 40000000):
            raise errors.IncorrectDamage

        if comment and len(comment) > 40:
            raise errors.IncorrectComment

        form = await self.api.get_form(data["i"])
        boss_data = await self.api.get_boss(data["i"], data["w"], data["b"])
        user_data = await self.api.get_user(ctx.author)

        record = await self.api.post_record(
            data["i"],
            data["w"],
            data["b"],
            data["s"],
            user_data["id"],
            record_id=data["r"],
            month=form["month"],
            damage=damage,
            comment=comment,
        )

        embed = self.embedMaker.record_finish(form, data["w"], boss_data, data["s"], record, user_data)

        await ctx.state.set_user({"clan.finish_record": ""}, unset=True)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Clan(bot))
    bot.add_cog(ClanResponse(bot))
    bot.add_cog(Cbre(bot))