from discord.ext.commands import Context, command

from mechadon import deepseek

from . import BaseCog


class SummarizeCog(BaseCog):
    @command("summarize")
    async def summarize(self, context: Context):
        messages = [
            message
            async for message in context.channel.history(
                limit=100, before=context.message
            )
        ]
        messages.reverse()

        log = "\n".join(
            f"{message.author.display_name} — {message.created_at.strftime('%I:%M %p')}\n{message.content}"
            for message in messages
            if message.content
        )

        async with context.typing():
            result = deepseek.summarize(log)

        await self.reply(context, result)
