from discord_slash import SlashCommand


def _get_val(d: dict, key):
    try:
        value = d[key]
    except KeyError:
        value = d[None]
    return value


class CustomSlashCommand(SlashCommand):
    """
    A rewrite of :class:`SlashCommand` to inject :class:`State`.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def invoke_command(self, func, ctx, args):
        """
        Invokes command.

        :param func: Command coroutine.
        :param ctx: Context.
        :param args: Args. Can be list or dict.
        """
        try:
            await self._discord.invoke_slash_command(func, ctx, args)
        except Exception as ex:
            if not await self._handle_invoke_error(func, ctx, ex):
                await self.on_slash_command_error(ctx, ex)

    async def invoke_component_callback(self, func, ctx):
        """
        Invokes component callback.

        :param func: Component callback object.
        :param ctx: Context.
        """
        try:
            await self._discord.invoke_component_callback(func, ctx)
        except Exception as ex:
            if not await self._handle_invoke_error(func, ctx, ex):
                await self.on_component_callback_error(ctx, ex)

    def get_component_callback(
        self,
        message_id: int = None,
        custom_id: str = None,
        component_type: int = None,
    ):
        """
        Returns component callback (or None if not found) for specific combination of message_id, custom_id, component_type.

        :param message_id: If specified, only removes the callback for the specific message ID.
        :type message_id: Optional[.model]
        :param custom_id: The ``custom_id`` of the component.
        :type custom_id: Optional[str]
        :param component_type: The type of the component. See :class:`.model.ComponentType`.
        :type component_type: Optional[int]

        :return: Optional[model.ComponentCallbackObject]
        """
        message_id_dict = self.components

        try:
            custom_id_dict = _get_val(message_id_dict, message_id)

            # add prefix support, e.g. "pref_custom.name__some.data" will call the function which custom_id equal to "pref_custom.name"
            if custom_id.startswith("pref_"):
                custom_id = custom_id[: custom_id.rfind("__")]

            component_type_dict = _get_val(custom_id_dict, custom_id)
            callback = _get_val(component_type_dict, component_type)

        except KeyError:  # there was no key in dict and no global fallback
            pass
        else:
            return callback
