from discord.ext.commands import Converter, Context

from mechadon import db


class RoleLenient(Converter):
    @staticmethod
    def sanitize(s: str):
        return s.lower().strip()

    @classmethod
    def get_alias(cls, context: Context, argument: str):
        argument = cls.sanitize(argument)
        return db.session.query(RoleAlias).filter(
            RoleAlias.alias.ilike(argument),
            RoleAlias.server_id == context.guild.id,
        ).first()

    @classmethod
    def get_role(cls, context: Context, argument: str):
        argument = cls.sanitize(argument)
        all_roles = context.guild.roles
        for role in all_roles:
            if cls.sanitize(role.name) == argument:
                return role
        if (alias := cls.get_alias(context, argument)):
            return discord.utils.find(
                lambda x: x.id == alias.role_id, all_roles
            )
        return None

    async def convert(self, context: Context, argument: str):
        role = self.get_role(context, argument)
        if not role:
            raise RoleNotFound(argument)
        return role
