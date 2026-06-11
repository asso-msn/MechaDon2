from discord.ext.commands import Context, command

from mechadon.cogs import BaseCog
from mechadon.formatters import member


class UnclesCog(BaseCog):
    @command()
    async def uncles(self, context: Context, maximum: int = 25):
        members = context.guild.members
        members.sort(key=lambda x: x.joined_at)

        await self.reply_list(
            context,
            members[:maximum],
            formatter=lambda x: f"{x.joined_at.date()}: {member(x)}",
            total=False,
        )
