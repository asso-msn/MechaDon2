import requests
import sqlalchemy as sa
from discord import Message

from mechadon import db

from . import BaseCog, Cog, Context, commands


class LogHook(db.Base):
    server_id = sa.Column(db.Id, primary_key=True)
    added_by = sa.Column(db.Id)
    webhook = sa.Column(sa.String, nullable=False)


class LogCog(BaseCog):
    @Cog.listener()
    async def on_message_delete(self, message: Message):
        if not message:
            return
        server = message.guild
        log_hooks = db.session.query(LogHook).filter_by(server_id=server.id)
        for hook in log_hooks:
            requests.post(
                hook.webhook,
                {
                    "content": f"[DELETED ({message.created_at})]\n{message.content}",
                    "username": f"{message.author} (#{message.channel})",
                    "avatar_url": message.author.avatar.url
                    if message.author.avatar
                    else None,
                },
            )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def log(self, context: Context, webhook_url):
        server = context.guild
        for hook in db.session.query(LogHook).filter_by(server_id=server.id):
            db.session.delete(hook)
        hook = LogHook(
            server_id=server.id, webhook=webhook_url, added_by=context.author.id
        )
        db.session.add(hook)
        db.session.commit()
        await self.reply(context, "Added", hook)
