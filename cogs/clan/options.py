from discord_slash.utils.manage_commands import create_choice
from discord_slash.utils.manage_components import create_button, create_actionrow, create_select, create_select_option
from discord_slash.model import ButtonStyle

status_choices = [
    create_choice(value=1, name="正式刀"),
    create_choice(value=2, name="補償刀"),
    create_choice(value=3, name="凱留刀"),
    create_choice(value=11, name="戰鬥中"),
    create_choice(value=12, name="等待中"),
    create_choice(value=13, name="等待@mention"),
    create_choice(value=21, name="完成(正式)"),
    create_choice(value=22, name="完成(補償)"),
    create_choice(value=23, name="暴死"),
    create_choice(value=24, name="求救"),
]

status_options = create_actionrow(
    *[
        create_select(
            placeholder="紀錄狀態",
            options=[
                create_select_option(
                    label="正式刀",
                    value="1",
                    emoji="\u26AA",
                ),
                create_select_option(
                    label="補償刀",
                    value="2",
                    emoji="\U0001F7E4",
                ),
                create_select_option(
                    label="凱留刀",
                    value="3",
                    emoji="\U0001F7E3",
                ),
                create_select_option(
                    label="戰鬥中",
                    value="11",
                    emoji="\U0001F7E0",
                ),
                create_select_option(
                    label="等待中",
                    value="12",
                    emoji="\U0001F535",
                ),
                create_select_option(
                    label="等待@mention",
                    value="13",
                    emoji="\U0001F535",
                ),
                create_select_option(
                    label="完成(正式)",
                    value="21",
                    emoji="\U0001F7E2",
                ),
                create_select_option(
                    label="完成(補償)",
                    value="22",
                    emoji="\U0001F7E2",
                ),
                create_select_option(
                    label="暴死",
                    value="23",
                    emoji="\U0001F534",
                ),
                create_select_option(
                    label="求救",
                    value="24",
                    emoji="\U0001F534",
                ),
            ],
        )
    ]
)

damage_buttons = create_actionrow(
    *[
        create_button(
            style=ButtonStyle.red,
            label="物理一刀",
            emoji="\U0001F52A",
        ),
        create_button(
            style=ButtonStyle.blue,
            label="魔法一刀",
            emoji="\U0001F52E",
        ),
        create_button(
            style=ButtonStyle.gray,
            label="自訂",
            emoji="\u270F",
        ),
    ]
)


boss_choices = [
    create_choice(value=1, name="一王"),
    create_choice(value=2, name="二王"),
    create_choice(value=3, name="三王"),
    create_choice(value=4, name="四王"),
    create_choice(value=5, name="五王"),
]

boss_buttons = create_actionrow(
    *[
        create_button(
            style=ButtonStyle.gray,
            label="一王",
        ),
        create_button(
            style=ButtonStyle.gray,
            label="二王",
        ),
        create_button(
            style=ButtonStyle.gray,
            label="三王",
        ),
        create_button(
            style=ButtonStyle.gray,
            label="四王",
        ),
        create_button(
            style=ButtonStyle.gray,
            label="五王",
        ),
    ]
)

week_buttons = create_actionrow(
    *[
        create_button(
            style=ButtonStyle.blue,
            label="上一周",
        ),
        create_button(
            style=ButtonStyle.blue,
            label="下一周",
        ),
    ]
)
