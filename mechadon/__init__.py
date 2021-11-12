import importlib
from pathlib import Path
from discord import Intents
from discord.ext.commands import Bot
from discord.mentions import AllowedMentions

from .config import Config


APP_DIR = Path(__file__).parent
intents = Intents.default()
intents.members = True
config = Config()
bot = Bot(
    command_prefix=config.prefix,
    allowed_mentions=AllowedMentions(everyone=False, roles=False),
    intents=intents,
)


def get_cogs_modules() -> dict:
    result = {}
    for file in (APP_DIR / 'cogs').glob('*'):
        if file.name.startswith('_'):
            continue
        name = file.name.removesuffix('.py')
        module = importlib.import_module(f'{__name__}.cogs.{name}')
        result[name] = module
    return result

def setup_cogs():
    for name, module in get_cogs_modules().items():
        cog = getattr(module, 'cog', None) or getattr(module, f'{name.title()}Cog')
        bot.add_cog(cog(bot=bot))

def run():
    setup_cogs()
    bot.run(config.token)

for module in get_cogs_modules().values():
    if hasattr(module, 'MODELS'):
        # Necessary for allowing alembic to discover models for automigration
        module.MODELS
