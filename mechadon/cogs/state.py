import requests
from discord import RawReactionActionEvent
from discord.ext import commands

from mechadon import db
from mechadon.cogs import BaseCog


class State(db.Base):
    server_id = db.Column(db.Id, nullable=False, primary_key=True)
    react = db.Column(db.String, nullable=False, primary_key=True)
    react_message_id = db.Column(db.Id)
    icon = db.Column(db.String)
    channel_id = db.Column(db.Id)
    channel_text = db.Column(db.String)
    message_id = db.Column(db.Id)
    message_text = db.Column(db.String)

    def __str__(self):
        return f"{self.__class__.__name__} {self.react}"


class StateCog(BaseCog):
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        if payload.user_id == self.bot.user.id:
            return
        state = (
            db.session.query(State)
            .filter_by(
                server_id=payload.guild_id,
                react=payload.emoji.name,
                react_message_id=payload.message_id,
            )
            .first()
        )
        if not state:
            return

        states = db.session.query(State).filter_by(
            server_id=payload.guild_id, channel_id=state.channel_id
        )
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(state.react_message_id)
        await message.clear_reactions()
        for s in states:
            await message.add_reaction(s.react)

        if state.channel_id and state.channel_text:
            channel = await self.bot.fetch_channel(state.channel_id)
            await channel.edit(name=state.channel_text)

        if state.icon:
            guild = self.bot.get_guild(payload.guild_id)
            content = requests.get(state.icon).content
            print("Awaiting guild update for icon...")
            await guild.edit(icon=content)
            print("Awaiting guild update finished!")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def state(self, context, react=None, key=None, *, value=None):
        if not react:
            return await self.state_list(context)
        return await self.edit_state(context, react, key, value)

    async def state_list(self, context):
        query = db.session.query(State).filter_by(server_id=context.guild.id)
        await self.reply_list(context, query)

    async def edit_state(self, context, react, key, value):
        state = (
            db.session.query(State)
            .filter_by(server_id=context.guild.id, react=react)
            .first()
        )
        if key:
            return await self.update_state(context, state, key, value)

        if state:
            db.session.delete(state)
            action = "Removed"
        else:
            state = State(server_id=context.guild.id, react=react)
            db.session.add(state)
            action = "Added"
        db.session.commit()
        await self.reply(context, action, state)

    async def update_state(self, context, state, key, value):
        if key == "icon":
            files = context.message.embeds + context.message.attachments
            if files:
                value = files[0].url
            else:
                value = value and value.strip("<>")

        if key == "react":
            value = value.split("/")[-1]
            key = "react_message_id"

        if key == "channel":
            value = value.split("/")[-1]
            key = "channel_id"

        if key == "name":
            key = "channel_text"

        setattr(state, key, value)
        db.session.commit()
        await self.reply(context, "Updated", state, key, "->", value)
