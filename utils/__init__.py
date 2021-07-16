from discord import User, Embed
from datetime import datetime
import random
from typing import NamedTuple
from utils.fetch_rank import FetchRank


class Unit(NamedTuple):
    id: int
    keyword: str
    name: str
    color: int


class GameDataVersion(NamedTuple):
    jp: dict
    tw: dict
    updateTime: str


class Counter:
    """
    Usage counter
    """

    def __init__(self):
        self._count = {
            "message_received": 0,
            "slash_received": 0,
            "component_received": 0,
        }  # let received counts show first

    def add(self, target: str):
        if self._count.get(target):
            self._count[target] += 1
        else:
            self._count.update({target: 1})

    def get(self, target: str):
        return self._count.get(target) or 0

    def set(self, target: str, num: int):
        self._count[target] = num

    def as_list(self):
        return self._count.items()

    def keys(self):
        return self.count.keys()


def create_embed(
    title: str = "",
    description: str = Embed.Empty,
    color="default",
    url: str = Embed.Empty,
    author: dict = None,
    footer: dict = None,
    thumbnail: str = Embed.Empty,
):
    if color == "default":
        color = 0x1BAED8
    elif color == "error":
        color = 0xE82E2E
    embed = Embed(title=title, description=description, color=color, url=url)
    if author:
        embed._author = author
    if footer:
        embed._footer = footer
    if thumbnail:
        embed._thumbnail = {"url": thumbnail}
    return embed


def error_embed(
    title: str,
    description: str = Embed.Empty,
    author: User = None,
    timestamp: datetime = None,
    tracking_uuid: str = "",
):
    if not timestamp:
        timestamp = datetime.utcnow()
    embed = Embed(title=title, color=0xE82E2E, description=description, timestamp=timestamp)
    embed.set_author(name="\U0001f6a8 ERROR Report")
    if author:
        embed.set_footer(
            text=f"Triggered by {author.name}#{author.discriminator}\n{tracking_uuid}", icon_url=author.avatar_url
        )

    return embed


def notice_embed(title: str, description: str = Embed.Empty, author: User = None, timestamp: datetime = None):
    if not timestamp:
        timestamp = datetime.utcnow()
    embed = Embed(title=title, color=0x1BAED8, description=description, timestamp=timestamp)
    embed.set_author(name="System")
    if author:
        embed.set_footer(text=f"by {author.name}#{author.discriminator}", icon_url=author.avatar_url)

    return embed


def how_to_use(correct: str):
    msgs = [f"請使用 `{correct}`", f"這功能要這樣用喔 `{correct}`", f"用錯方法了啦, 正確的用法是{correct}"]
    return random.choice(msgs)


def damage_converter(x: str = "0"):
    val = 0
    num_map = {"K": 1000, "W": 10000, "M": 1000000, "B": 1000000000}
    if x.isdigit():
        val = int(x)
    else:
        if len(x) > 1:
            val = float(x[:-1]) * num_map.get(x[-1].upper(), 1)
    return int(val)


def create_profile_embed(data: dict):
    if data["favorite_unit"]["unit_rarity"] == 6:
        unit_rarity_type = 60
    elif data["favorite_unit"]["unit_rarity"] >=3:
        unit_rarity_type = 30
    else:
        unit_rarity_type = 10
        
    unit_id = data["favorite_unit"]["id"] + unit_rarity_type
    embed = create_embed(
        title=data["user_info"]["user_name"],
        description=data["user_info"]["user_comment"],
        author={"name": "個人檔案"},
        thumbnail=f"https://randosoru.me/static/assets/character_unit/{unit_id}.webp",
        footer={"text": "此資料已快取且僅供參考"},
    )
    embed.add_field(name="主角等級", value=data["user_info"]["team_level"], inline=True)
    embed.add_field(name="全角色戰力", value=f'{data["user_info"]["total_power"]:,}', inline=True)
    embed.add_field(name="所屬戰隊", value=data["clan_name"] or "無所屬", inline=True)
    embed.add_field(name="解放角色數", value=data["user_info"]["unit_num"], inline=True)
    embed.add_field(name="解放劇情數", value=data["user_info"]["open_story_num"], inline=True)
    embed.add_field(
        name="露娜之塔完成樓層",
        value=f'{"-" if data["user_info"]["tower_cleared_floor_num"] == -1 else data["user_info"]["tower_cleared_floor_num"]} / {"-" if data["user_info"]["tower_cleared_ex_quest_count"] == -1 else data["user_info"]["tower_cleared_ex_quest_count"]}',
        inline=True,
    )
    embed.add_field(
        name="戰鬥競技場排名",
        value=data["user_info"]["arena_rank"] or "-",
        inline=True,
    )
    embed.add_field(
        name="公主競技場排名",
        value=data["user_info"]["grand_arena_rank"] or "-",
        inline=True,
    )
    # embed.timestamp = datetime.utcfromtimestamp(data["cacheTs"])
    return embed


async def fakeDefer():
    pass
