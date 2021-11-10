from io import BytesIO
from discord import File, Message
from discord.ext.commands.errors import CommandError
import sqlalchemy as sa
import requests

from mechadon import db
from . import BaseCog, Cog, Context, commands


class Autoreply(db.Base):
    __tablename__ = 'autoreplies'

    trigger = sa.Column(sa.String, nullable=False, primary_key=True)
    partial = sa.Column(sa.Boolean, default=False)
    added_by = sa.Column(db.Id)
    server_id = sa.Column(db.Id, nullable=False, primary_key=True)
    text = sa.Column(sa.String)
    file_url = sa.Column(sa.String)

    def matches(self, s: str):
        s = s.lower()
        trigger = self.trigger.lower()
        if not self.partial:
            return trigger == s
        return trigger in s.split()

    def get_file(self) -> File:
        if not self.file_url:
            return None
        response = requests.get(self.file_url)
        return File(BytesIO(response.content), self.file_url.split('/')[-1])



class AutoreplyCog(BaseCog):
    @staticmethod
    def get_autoreplies(guild):
        return db.session.query(Autoreply).filter_by(server_id=guild.id)

    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
        for sticker in self.get_autoreplies(message.guild):
            if not sticker.matches(message.content):
                continue
            with message.channel.typing():
                await message.reply(sticker.text, file=sticker.get_file())
            message.channel.typing

    @commands.command('reply')
    @commands.has_permissions(administrator=True)
    async def add_reply(self, context: Context, name, *, text = None):
        if (embeds := context.message.embeds):
            url = embeds[0].url
            text = None
        elif text:
            url = None
        elif (autoreply_db := self.get_autoreplies(context.guild).filter_by(trigger=name).first()):
            db.session.delete(autoreply_db)
            db.session.commit()
            await self.reply(context, 'Deleted reply', name)
            return
        else:
            raise CommandError('Can not be empty, provide either text or file')
        db.update_or_create(
            Autoreply,
            trigger=name,
            server_id=context.guild.id,
            file_url=url,
            text=text,
            added_by=context.author.id,
            filter_keys=['trigger', 'server'],
        )
        db.session.commit()
        await self.reply(context, 'Reply', name, 'added')

    @commands.command()
    async def replies(self, context: Context):
        triggers = [x.trigger for x in self.get_autoreplies(context.guild)]
        await self.reply(context, *triggers, sep='\n')
