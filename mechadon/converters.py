from typing import Union

import discord
from discord import TextChannel, User
from discord.ext.commands import BadArgument, Context, Converter
from discord.ext.commands.errors import ChannelNotFound, RoleNotFound

from mechadon import db
from mechadon.models import RoleAlias


class ChannelConverter(Converter):
    async def convert(self, ctx: Context, argument: str) -> TextChannel:
        if argument.startswith("<#") and argument.endswith(">"):
            argument = argument[2:-1]

        if argument.isdigit():
            if channel := ctx.bot.get_channel(int(argument)):
                return channel

        if ctx.guild:
            for channel in ctx.guild.text_channels:
                if channel.name == argument:
                    return channel

        raise ChannelNotFound(argument)


class ChannelOrUser(ChannelConverter):
    async def convert(
        self, ctx: Context, argument: str
    ) -> Union[TextChannel, User]:
        raw = argument
        if raw.startswith("<@") and raw.endswith(">"):
            raw = raw[2:-1].lstrip("!")
            if raw.isdigit():
                if user := ctx.bot.get_user(int(raw)):
                    return user
            raise BadArgument(f'Could not resolve "{argument}" as a user.')

        try:
            return await super().convert(ctx, argument)
        except ChannelNotFound:
            pass

        if argument.isdigit():
            if user := ctx.bot.get_user(int(argument)):
                return user

        raise BadArgument(
            f'Could not resolve "{argument}" as a channel or user.'
        )


class RoleLenient(Converter):
    @staticmethod
    def sanitize(s: str):
        return s.lower().strip()

    @classmethod
    def get_alias(cls, context: Context, argument: str):
        argument = cls.sanitize(argument)
        return (
            db.session.query(RoleAlias)
            .filter(
                RoleAlias.alias.ilike(argument),
                RoleAlias.server_id == context.guild.id,
            )
            .first()
        )

    @classmethod
    def get_role(cls, context: Context, argument: str):
        argument = cls.sanitize(argument)
        all_roles = context.guild.roles
        for role in all_roles:
            if cls.sanitize(role.name) == argument:
                return role
        if alias := cls.get_alias(context, argument):
            return discord.utils.find(
                lambda x: x.id == alias.role_id, all_roles
            )
        return None

    async def convert(self, context: Context, argument: str):
        role = self.get_role(context, argument)
        if not role:
            raise RoleNotFound(argument)
        return role
