import importlib
from pathlib import Path
from discord.ext.commands import Bot, Cog

from .config import Config


APP_DIR = Path(__file__).parent

config = Config()
bot = Bot(command_prefix=config.prefix)


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
