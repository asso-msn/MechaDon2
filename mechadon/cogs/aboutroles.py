from discord.ext.commands import Context, command

from mechadon.cogs import BaseCog
from mechadon.converters import RoleLenient
from mechadon.formatters import member


class AboutrolesCog(BaseCog):
    @command()
    async def whois(self, context: Context, *, role: RoleLenient):
        await self.reply_list(context, role.members, formatter=member)

    @command()
    async def toproles(self, context: Context, maximum: int = 10):
        roles = [(len(x.members), x) for x in context.guild.roles]
        roles.sort(key=lambda x: x[0], reverse=True)
        roles = roles[:maximum]

        def formatter(x):
            return f"{x[0]}: {x[1]}"

        await self.reply_list(
            context, roles, formatter=formatter, sort=False, total=False
        )
