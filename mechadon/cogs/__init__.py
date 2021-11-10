from discord import Bot
from discord.ext.commands import Cog, Context

class BaseCog(Cog):
    def __init__(self, bot: Bot = None):
        self.bot = bot

    async def reply(self, context: Context, *words, sep=' '):
        msg = sep.join(map(str, words)) or '*Empty*'
        return await context.reply(msg)

    @staticmethod
    def get_roles_by_id(context):
        return {x.id: x for x in context.guild.roles}

from discord.ext import commands
