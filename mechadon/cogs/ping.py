from . import BaseCog, Context, commands


class PingCog(BaseCog):
    @commands.command()
    async def ping(self, context: Context):
        await context.reply('pong!')
