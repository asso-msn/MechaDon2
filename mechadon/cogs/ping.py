from datetime import datetime

from . import BaseCog, Context, commands


class PingCog(BaseCog):
    @commands.command()
    async def ping(self, context: Context):
        delta = datetime.utcnow().second - context.message.created_at.second
        await context.reply(
            '```'
            '\nPING Discord 56(84) bytes of data.'
            f'\n64 bytes from Discord: icmp_seq=1 ttl=56 time={delta / 1000}'
            '```'
        )
