import random
import re
from io import BytesIO

import requests
import sqlalchemy as sa
from discord import File, Message
from discord.ext.commands import Cog, Context, command, has_permissions
from discord.ext.commands.errors import CommandError

from mechadon import db
from mechadon.cogs import BaseCog


class Autoreply(db.Base):
    __tablename__ = "autoreplies"

    trigger = sa.Column(sa.String, nullable=False, primary_key=True)
    partial = sa.Column(sa.Boolean, default=False)
    added_by = sa.Column(db.Id)
    server_id = sa.Column(db.Id, nullable=False, primary_key=True)
    text = sa.Column(sa.String)
    random = sa.Column(sa.Integer)

    def matches(self, s: str):
        s = s.lower()
        if self.trigger.startswith("`/") and self.trigger.endswith("/`"):
            return re.match(self.trigger[2:-2], s)
        trigger = self.trigger.lower()
        if not self.partial:
            return trigger == s
        return trigger in s.split()


class AutoreplyCog(BaseCog):
    @staticmethod
    def get_autoreplies(guild):
        return db.session.query(Autoreply).filter_by(server_id=guild.id)

    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
        for reply in self.get_autoreplies(message.guild):
            if not reply.matches(message.content):
                continue
            if reply.random:
                if random.randint(1, reply.random) != 1:
                    continue
            with message.channel.typing():
                await message.reply(reply.text)

    @command("reply")
    @has_permissions(administrator=True)
    async def add_reply(self, context: Context, name, *, text=None):
        text = text or ""
        files = context.message.embeds + context.message.attachments
        if files:
            urls = " ".join(x.url for x in files)
            if text:
                text += "\n" + urls
            else:
                text = urls
        if not text:
            autoreply_db = (
                self.get_autoreplies(context.guild)
                .filter_by(trigger=name)
                .first()
            )
            if not autoreply_db:
                return await self.reply(context, "No such reply to delete")
            db.session.delete(autoreply_db)
            db.session.commit()
            return await self.reply(context, "Deleted reply", name)

        db.update_or_create(
            Autoreply,
            trigger=name,
            server_id=context.guild.id,
            text=text,
            added_by=context.author.id,
            filter_keys=["trigger", "server"],
        )
        db.session.commit()
        await self.reply(context, "Reply", name, "added")

    @command()
    async def replies(self, context: Context):
        triggers = [x.trigger for x in self.get_autoreplies(context.guild)]
        await self.reply(context, *triggers, sep="\n")
