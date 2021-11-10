from discord import TextChannel
from . import BaseCog, Context, commands


class TopicCog(BaseCog):
    @commands.command()
    async def topic(self, context: Context, channel: TextChannel = None):
        channel = channel or context.channel
        msg = channel.topic or '*empty*'
        await context.send(msg)
