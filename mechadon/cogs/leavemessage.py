from discord import TextChannel, Member
import sqlalchemy as sa

from mechadon import db, formatters
from . import BaseCog, Cog, Context, commands


class LeaveMessageChannel(db.Base):
    channel_id = sa.Column(db.Id, nullable=False, primary_key=True)
    server_id = sa.Column(db.Id, nullable=False, primary_key=True)
    added_by = sa.Column(db.Id)


class LeavemessageCog(BaseCog):
    @staticmethod
    def get_leave_message_channels(guild):
        return db.session.query(LeaveMessageChannel).filter_by(server_id=guild.id)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def leavechan(self, context: Context, *, channel: TextChannel = None):
        channel = channel or context.channel
        if entry := (db.session.get(LeaveMessageChannel, (channel.id, channel.guild.id))):
            db.session.delete(entry)
            db.session.commit()
            await self.reply(context, f'Channel {channel} will no longer display leaves')
            return
        entry = LeaveMessageChannel(channel_id=channel.id, server_id=channel.guild.id, added_by=context.author.id)
        db.session.add(entry)
        db.session.commit()
        await self.reply(context, f'Channel {channel} will now display leaves')

    @Cog.listener()
    async def on_member_remove(self, member: Member):
        entries = self.get_leave_message_channels(member.guild)
        member_str = formatters.member(member)
        for entry in entries:
            channel = self.bot.get_partial_messageable(entry.channel_id)
            await channel.send(f'{member_str} just left the server.')
