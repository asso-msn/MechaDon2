import sqlalchemy as sa
from discord import Message, MessageType, TextChannel
from discord.ext.commands import Cog, command, has_permissions

from mechadon import db
from mechadon.cogs import BaseCog, Context


class Autoreact(db.Base):
    server_id = sa.Column(db.Id, nullable=False, primary_key=True)
    channel_id = sa.Column(db.Id, nullable=False, primary_key=True)
    react = sa.Column(sa.String, nullable=False, primary_key=True)

    def __str__(self):
        if self.channel_id != "welcome":
            channel_url = f"https://discord.com/channels/{self.server_id}/{self.channel_id}"
        else:
            channel_url = "welcome"
        return f"{self.__class__.__name__} {self.react} in {channel_url}"


class AutoreactsCog(BaseCog):
    @Cog.listener()
    async def on_message(self, message: Message):
        if message.type == MessageType.new_member:
            react = db.session.query(Autoreact).filter_by(
                server_id=message.guild.id, channel_id="welcome"
            )
            for row in react:
                await message.add_reaction(row.react)
            return

        if message.type == MessageType.default:
            for row in db.session.query(Autoreact).filter_by(
                server_id=message.guild.id, channel_id=message.channel.id
            ):
                await message.add_reaction(row.react)
            return

    @command()
    @has_permissions(administrator=True)
    async def react(
        self, context: Context, react: str = None, channel: TextChannel = None
    ):

        if not react:
            return await self.list_reacts(context, channel)
        return await self.toggle_react(context, react, channel)

    @command()
    @has_permissions(administrator=True)
    async def welcome(self, context: Context, react: str = None):
        react = react or "👋"
        await self.toggle_react(context, react, channel="welcome")

    async def list_reacts(self, context: Context, channel: TextChannel = None):
        query = db.session.query(Autoreact).filter_by(
            server_id=context.guild.id
        )
        if channel:
            query = query.filter_by(channel_id=channel.id)

        reacts = query.all()
        if not reacts:
            return await self.reply(context, "No autoreacts found")

        await self.reply_list(context, reacts)

    async def toggle_react(
        self, context: Context, react: str, channel: TextChannel = None
    ):
        channel = channel or context.channel
        if channel == "welcome":
            channel_id = channel
        else:
            channel_id = channel.id

        if (
            obj := db.session.query(Autoreact)
            .filter_by(
                server_id=context.guild.id, channel_id=channel_id, react=react
            )
            .first()
        ):
            db.session.delete(obj)
            db.session.commit()
            await self.reply(context, f"Removed autoreact {obj}")
            return

        obj = Autoreact(
            server_id=context.guild.id,
            channel_id=channel_id,
            react=react,
        )
        db.session.add(obj)
        db.session.commit()
        await self.reply(context, f"Added {obj}")
