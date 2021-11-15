from discord.ext.commands.errors import CommandError, CommandNotFound
from . import BaseCog, Cog, Context


class CoreCog(BaseCog):
    @Cog.listener()
    async def on_ready(self):
        sep = '------'
        print(f'Logged in as {self.bot.user} (ID: {self.bot.user.id})')
        print(sep)
        print(f'Loaded cogs: {", ".join(self.bot.cogs.keys())}')
        print(sep)

    @Cog.listener()
    async def on_command_error(self, context: Context, error: Exception):
        if isinstance(error, CommandNotFound):
            raise error
        if isinstance(error, CommandError):
            await self.reply(context, error)
        else:
            await self.reply(context, 'An error occured')
        raise error
