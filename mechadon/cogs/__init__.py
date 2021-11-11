from discord import Bot, Embed
from discord.ext.commands import Cog, Context
from discord.mentions import AllowedMentions

class BaseCog(Cog):
    def __init__(self, bot: Bot = None):
        self.bot = bot

    async def reply(self, context: Context, *words, sep=' ', sort=False):
        words = list(map(str, words))
        if sort:
            words.sort(key=lambda x: x.lower())
        msg = sep.join(words) or '*Empty*'
        embed = Embed(description=msg)
        return await context.reply(embed=embed, allowed_mentions=AllowedMentions.none())

    @staticmethod
    def get_roles_by_id(context):
        return {x.id: x for x in context.guild.roles}

from discord.ext import commands
