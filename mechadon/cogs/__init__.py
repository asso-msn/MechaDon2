from discord import Bot, Embed
from discord.ext.commands import Cog, Context
from discord.mentions import AllowedMentions

class BaseCog(Cog):
    MAX_MESSAGE_LENGTH = 4096

    def __init__(self, bot: Bot = None):
        self.bot = bot
        super().__init__()

    async def reply(
        self,
        context: Context,
        *words,
        list_=None,
        formatter=str,
        sep=' ',
        sort=False,
        total=False
    ):
        if list_:
            words = list_
        words = list(map(formatter, words))
        if sort:
            words.sort(key=lambda x: x.lower())
        msg = sep.join(words) or '*Empty*'
        if total:
            msg = f'Total: {len(words)}\n\n' + msg
        if len(msg) > self.MAX_MESSAGE_LENGTH:
            msg = msg[:self.MAX_MESSAGE_LENGTH - 2] + '\n…'
        embed = Embed(description=msg)
        return await context.reply(embed=embed, allowed_mentions=AllowedMentions.none())

    async def reply_list(self, context: Context, list_, **kwargs):
        kwargs.setdefault('sep', '\n')
        kwargs.setdefault('sort', True)
        kwargs.setdefault('total', True)
        return await self.reply(context, *list_, **kwargs)

    @staticmethod
    def get_roles_by_id(context):
        return {x.id: x for x in context.guild.roles}

from discord.ext import commands
