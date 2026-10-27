import sqlalchemy as sa
from discord import Member, TextChannel

from mechadon import db, formatters

from . import BaseCog, Cog, Context, commands


class Doorway(db.Base):
    channel_id = sa.Column(db.Id, nullable=False, primary_key=True)
    server_id = sa.Column(db.Id, nullable=False, primary_key=True)
    event = sa.Column(sa.String, nullable=False, primary_key=True)
    added_by = sa.Column(db.Id)


class DoorwayCog(BaseCog):
    """Announce members crossing the server's doorway."""

    @staticmethod
    def get_channels(guild, event):
        return db.session.query(Doorway).filter_by(
            server_id=guild.id, event=event
        )

    async def toggle_channel(self, context: Context, event, channel=None):
        channel = channel or context.channel
        entry = db.session.get(Doorway, (channel.id, channel.guild.id, event))
        if entry:
            db.session.delete(entry)
            db.session.commit()
            await self.reply(
                context,
                f"Channel {channel} will no longer display {event}s",
            )
            return
        db.session.add(
            Doorway(
                channel_id=channel.id,
                server_id=channel.guild.id,
                event=event,
                added_by=context.author.id,
            )
        )
        db.session.commit()
        await self.reply(
            context, f"Channel {channel} will now display {event}s"
        )

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def leavechan(self, context: Context, *, channel: TextChannel = None):
        """Toggle announcements of members leaving the server."""
        await self.toggle_channel(context, "leave", channel)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def joinchan(self, context: Context, *, channel: TextChannel = None):
        """Toggle announcements of members joining the server."""
        await self.toggle_channel(context, "join", channel)

    async def announce(self, member: Member, event: str, action: str):
        member_str = formatters.member(member)
        for entry in self.get_channels(member.guild, event):
            channel = self.bot.get_partial_messageable(entry.channel_id)
            await channel.send(f"{member_str} ({member.mention}) {action}")

    @Cog.listener()
    async def on_member_remove(self, member: Member):
        await self.announce(member, "leave", "just left the server.")

    @Cog.listener()
    async def on_member_join(self, member: Member):
        await self.announce(member, "join", "just joined the server.")
