from discord_slash.model import ButtonStyle
from main import AIKyaru
from discord.ext import commands
from discord_slash.context import ComponentContext
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_components import create_actionrow, create_button, create_select, create_select_option
from copy import deepcopy


character_options = create_actionrow(
    *[
        create_select(
            placeholder="角色資訊預設頁面",
            custom_id="user.preferences.character_default_type",
            options=[
                create_select_option(
                    label="簡介",
                    description="預設顯示角色簡介",
                    value="1",
                    emoji={"name": "info", "id": 850732950600679464},
                ),
                create_select_option(
                    label="專武",
                    description="預設顯示角色專用武器",
                    value="2",
                    emoji={"name": "ue", "id": 850732950642884608},
                ),
                create_select_option(
                    label="技能",
                    description="預設顯示角色技能",
                    value="3",
                    emoji={"name": "skill", "id": 850732950847881226},
                ),
                create_select_option(
                    label="攻擊",
                    description="預設顯示角色攻擊模式",
                    value="4",
                    emoji={"name": "icon_skill_attack", "id": 605337612835749908},
                ),
                create_select_option(
                    label="RANK推薦",
                    description="預設顯示推薦的Rank",
                    value="5",
                    emoji={"name": "rank", "id": 850732950525575178},
                ),
            ],
        )
    ]
)
unlink_button = create_actionrow(*[create_button(style=ButtonStyle.red, label="解除遊戲ID綁定", custom_id="user.unlink_uid")])


class UserPreferences(commands.Cog):
    def __init__(self, bot: AIKyaru):
        self.bot = bot

    @cog_ext.cog_slash(name="preferences", description="偏好設定")
    async def cog_preferences(self, ctx: SlashContext):
        type = await ctx.state.get_user(keys=["config", "character_default_type"]) or 1

        options = deepcopy(character_options)
        options["components"][0]["options"][type - 1]["default"] = True

        components = [options]

        if await ctx.state.get_user(keys=["linked_uid"]):
            components.append(unlink_button)

        await ctx.send(content="**偏好設定**", components=components, hidden=True)

    @cog_ext.cog_component(components="user.preferences.character_default_type")
    async def preferences_default_type(self, ctx: ComponentContext):
        type = int(ctx.selected_options[0])
        user_config = await ctx.state.get_user(keys=["config"]) or {}
        user_config["character_default_type"] = type
        await ctx.state.set_user({"config": user_config})

        options = deepcopy(character_options)
        options["components"][0]["options"][type - 1]["default"] = True

        components = [options]

        if await ctx.state.get_user(keys=["linked_uid"]):
            components.append(unlink_button)

        await ctx.edit_origin(content="**偏好設定**", components=components)

    @cog_ext.cog_component(components="user.unlink_uid")
    async def unlink_uid(self, ctx: ComponentContext):
        await ctx.state.set_user({"linked_uid": ""}, unset=True)

        type = await ctx.state.get_user(keys=["config", "character_default_type"]) or 1
        options = deepcopy(character_options)
        options["components"][0]["options"][type - 1]["default"] = True

        await ctx.edit_origin(content="**偏好設定**", components=[options])
        await ctx.send("已解除綁定", hidden=True)
