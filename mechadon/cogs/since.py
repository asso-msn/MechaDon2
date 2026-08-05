import time

from discord import Forbidden, Message, RawReactionActionEvent
from discord.ext.commands import Cog, Context, command

from mechadon.cogs import BaseCog

CHECK = "✅"


def format_message(something: str, user) -> str:
    return (
        f"<t:{int(time.time())}:R> since {something}\n"
        f"-# last edited by: {user.mention}"
    )


def parse_since(content: str) -> str | None:
    line = content.split("\n", 1)[0]
    if not line.startswith("<t:"):
        return None
    end = line.find(">")
    if end == -1:
        return None
    rest = line[end + 1 :]
    prefix = " since "
    if not rest.startswith(prefix):
        return None
    return rest[len(prefix) :]


class SinceCog(BaseCog):
    @command()
    async def since(self, context: Context, *, something: str):
        channel = context.channel
        content = format_message(something, context.author)
        try:
            await context.message.delete()
        except Exception:
            message = await context.reply(content)
        else:
            message = await channel.send(content)
        await self.react(message)

    @Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return
        if payload.emoji.name != CHECK:
            return

        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        if message.author != self.bot.user:
            return
        something = parse_since(message.content)
        if something is None:
            return

        guild = self.bot.get_guild(payload.guild_id)
        content = format_message(something, payload.member)
        if channel.permissions_for(guild.me).manage_messages:
            await message.clear_reactions()
            await message.edit(content=content)
            await self.react(message)
            return

        try:
            await message.delete()
        except Forbidden:
            pass
        new_message = await channel.send(content)
        await self.react(new_message)

    async def react(self, message: Message):
        try:
            await message.add_reaction(CHECK)
        except Forbidden:
            pass
