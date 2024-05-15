import re

import requests
import sqlalchemy as sa
from discord import Message, MessageType, TextChannel

from mechadon import db

from . import BaseCog, Cog, Context, commands


def escape_links(x: str):
    return re.sub(r"\bhttps?://\S*\b", r"<\g<0>>", x)


class Bridge(db.Base):
    name = sa.Column(sa.String, nullable=False, primary_key=True)
    channel_id = sa.Column(db.Id, nullable=False, primary_key=True)
    webhook = sa.Column(sa.String)


class BridgeCog(BaseCog):
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def bridge(
        self,
        context: Context,
        name=None,
        webhook_url=None,
        channel: TextChannel = None,
    ):
        channel = channel or context.channel
        bridge_db = (
            db.session.query(Bridge).filter_by(channel_id=channel.id).first()
        )
        if bridge_db:
            db.session.delete(bridge_db)
            action = "Removed"
        else:
            if not name:
                raise Exception("You must name the bridge")
            bridge_db = Bridge(
                name=name, channel_id=channel.id, webhook=webhook_url
            )
            db.session.add(bridge_db)
            action = "Added"
        db.session.commit()
        await self.reply(context, action, bridge_db)

    @Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return
        incoming_bridge = (
            db.session.query(Bridge)
            .filter_by(channel_id=message.channel.id)
            .first()
        )
        if not incoming_bridge:
            return
        outcoming_bridges = db.session.query(Bridge).filter_by(
            name=incoming_bridge.name
        )
        content = message.clean_content
        if message.type == MessageType.reply:
            replies_to = await message.channel.fetch_message(
                message.reference.message_id
            )
            if not replies_to.author.bot:
                author = replies_to.author.display_name
            else:
                author = str(replies_to.author)
                if "#" in author and "(" in author and ")" in author:
                    last_paren = author.rfind("(")
                    author = author[:last_paren].strip()

            content = (
                f"Replying to {author}:\n"
                + "> "
                + "\n> ".join(
                    escape_links(replies_to.clean_content).split("\n")
                )
                + "\n\n"
                + content
            )
        for attachment in message.attachments:
            content += f"\n{attachment.url}"
        for bridge in outcoming_bridges:
            if bridge == incoming_bridge:
                continue
            if not bridge.webhook:
                continue
            requests.post(
                bridge.webhook,
                {
                    "content": content,
                    "username": f"{message.author.display_name} (#{message.channel} @ {message.guild})",
                    "avatar_url": (
                        message.author.avatar.url
                        if message.author.avatar
                        else None
                    ),
                },
            )
