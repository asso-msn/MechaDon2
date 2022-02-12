from discord import TextChannel, Message
import requests
import sqlalchemy as sa

from . import BaseCog, Cog, Context, commands
from mechadon import db


class Bridge(db.Base):
    name = sa.Column(sa.String, nullable=False, primary_key=True)
    channel_id = sa.Column(db.Id, nullable=False, primary_key=True)
    webhook = sa.Column(sa.String)


class BridgeCog(BaseCog):
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def bridge(self, context: Context, name=None, webhook_url=None, channel: TextChannel = None):
        channel = channel or context.channel
        bridge_db = db.session.query(Bridge).filter_by(channel_id=channel.id).first()
        if bridge_db:
            db.session.delete(bridge_db)
            action = 'Removed'
        else:
            if not name:
                raise Exception('You must name the bridge')
            bridge_db = Bridge(name=name, channel_id=channel.id, webhook=webhook_url)
            db.session.add(bridge_db)
            action = 'Added'
        db.session.commit()
        await self.reply(context, action, bridge_db)

    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
        incoming_bridge = db.session.query(Bridge).filter_by(channel_id=message.channel.id).first()
        if not incoming_bridge:
            return
        outcoming_bridges = db.session.query(Bridge).filter_by(name=incoming_bridge.name)
        for bridge in outcoming_bridges:
            if bridge == incoming_bridge:
                continue
            if not bridge.webhook:
                continue
            requests.post(bridge.webhook, {
                'content': message.clean_content,
                'username': f'{message.author} (#{message.channel} @ {message.guild})',
                'avatar_url': message.author.avatar.url if message.author.avatar else None,
            })
