from discord import Cog
from discord.ext.commands import CommandError, CommandNotFound, Context

from mechadon.cogs import BaseCog


class CoreCog(BaseCog):
    @Cog.listener()
    async def on_ready(self):
        sep = "------"
        print(f"Logged in as {self.bot.user} (ID: {self.bot.user.id})")
        print(sep)
        print(f'Loaded cogs: {", ".join(self.bot.cogs.keys())}')
        print(sep)
        print(f"Servers: {self.bot.guilds}")
        print(sep)

    @Cog.listener()
    async def on_command_error(self, context: Context, error: Exception):
        if isinstance(error, CommandNotFound):
            raise error
        if isinstance(error, CommandError):
            await self.reply(context, error)
        else:
            await self.reply(context, "An error occured")
        raise error
