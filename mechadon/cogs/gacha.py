import random
import secrets

from . import BaseCog, commands


class GachaCog(BaseCog):
    @commands.group()
    async def gacha(self, context):
        pass

    @gacha.command()
    async def genesis(self, context):
        url = "https://fairyjoke.net/sdvx/genesis/gacha/card.png"
        url += "?salt=" + secrets.token_urlsafe(16)
        url += f"&id={random.randint(0, 1000000000)}"
        await context.send(url)
