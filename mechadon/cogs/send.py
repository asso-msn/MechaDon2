from discord import TextChannel
from discord.ext.commands import CheckFailure, Context, command, has_permissions

import mechadon
from mechadon.cogs import BaseCog
from mechadon.converters import ChannelConverter, ChannelOrUser

SENDAS_AVATAR = "https://discord.com/assets/18e336a74a159cfd.png"


def _find_user_avatar(context: Context, query: str) -> str | None:
    bot = context.bot
    if query.isdigit():
        user = bot.get_user(int(query))
        if user and user.avatar:
            return user.avatar.url
    query_lower = query.lower()
    for guild in bot.guilds:
        for member in guild.members:
            if (
                member.name.lower() == query_lower
                or member.display_name.lower() == query_lower
            ):
                if member.avatar:
                    return member.avatar.url
    return None


async def _check_cross_server(context: Context, destination: TextChannel):
    if destination.guild == context.guild:
        return
    author = context.author
    if author.id in mechadon.config.bot_admin_user_ids:
        return
    dest_member = destination.guild.get_member(author.id)
    if dest_member and dest_member.guild_permissions.administrator:
        return
    raise CheckFailure(
        "Cross-server send requires you to be an administrator in the"
        " destination server or a bot admin."
    )


class SendCog(BaseCog):
    @command()
    @has_permissions(administrator=True)
    async def send(
        self,
        context: Context,
        destination: ChannelOrUser,
        *,
        message: str,
    ):
        if isinstance(destination, TextChannel):
            await _check_cross_server(context, destination)
        await destination.send(message)

    @command()
    @has_permissions(administrator=True)
    async def sendas(
        self,
        context: Context,
        name: str,
        destination: ChannelConverter,
        *,
        message: str,
    ):
        await _check_cross_server(context, destination)
        avatar_url = SENDAS_AVATAR
        first_word, _, rest = message.partition(" ")
        if first_word.startswith("avatar="):
            raw_avatar = first_word[len("avatar=") :]
            message = rest
            if raw_avatar.startswith("http://") or raw_avatar.startswith(
                "https://"
            ):
                avatar_url = raw_avatar
            else:
                avatar_url = (
                    _find_user_avatar(context, raw_avatar) or SENDAS_AVATAR
                )
        webhook = await destination.create_webhook(name=name)
        try:
            await webhook.send(
                message,
                username=name,
                avatar_url=avatar_url,
            )
        finally:
            await webhook.delete()
