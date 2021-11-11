from discord.ext.commands.errors import CommandError
import sqlalchemy as sa
from discord import Role

from mechadon import db
from mechadon.converters import RoleLenient
from mechadon.models import RoleAlias
from . import BaseCog, Context, commands


class SelfRole(db.Base):
    role_id = sa.Column(db.Id, nullable=False, primary_key=True)
    server_id = sa.Column(db.Id, nullable=False, primary_key=True)
    added_by = sa.Column(db.Id)

    def __init__(self, *args, **kwargs):
        if (role := kwargs.pop('role')):
            kwargs['role_id'] = role.id
            kwargs['server_id'] = role.guild.id
        super().__init__(*args, **kwargs)


class SelfroleCog(BaseCog):
    @staticmethod
    def get_selfrole(role: Role):
        return db.session.get(SelfRole, (role.id, role.guild.id))

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def roletoggle(self, context: Context, *, role: RoleLenient):
        selfrole = self.get_selfrole(role)
        if not selfrole:
            selfrole = SelfRole(role=role, added_by=context.author.id)
            db.session.add(selfrole)
            action = 'Added'
        else:
            db.session.delete(selfrole)
            action = 'Removed'
        db.session.commit()
        await self.reply(context, action, selfrole)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def alias(self, context: Context, alias: str, *, role: RoleLenient = None):
        alias_db = RoleLenient.get_alias(context, alias)
        if role is None:
            if not alias_db:
                raise CommandError(f'Can not remove alias {alias} as it does not exist')
            db.session.delete(alias_db)
            db.session.commit()
            await self.reply(context, 'Removed alias', alias)
            return
        action = 'Updated' if alias_db else 'Added'
        alias_db = db.update_or_create(
            RoleAlias,
            role_id=role.id,
            server_id=context.guild.id,
            alias=alias,
            added_by=context.author.id,
            filter_keys=['alias', 'server_id'],
        )
        db.session.commit()
        await self.reply(context, action, alias_db)


    @commands.command()
    async def role(self, context: Context, *, role: RoleLenient):
        selfrole = self.get_selfrole(role)
        if not selfrole:
            raise CommandError(f'Role {role} is not a selfrole')
        if role in context.author.roles:
            await context.author.remove_roles(role)
            await self.reply(context, 'You no longer have role', role)
        else:
            await context.author.add_roles(role)
            await self.reply(context, 'You now have role', role)

    @commands.command()
    async def roles(self, context: Context):
        role_ids = [x.id for x in context.guild.roles]
        roles_db = db.session.query(SelfRole).filter(
                SelfRole.role_id.in_(role_ids)
        ).all()
        roles = filter(
            lambda x: x.id in [r.role_id for r in roles_db],
            context.guild.roles
        )
        await self.reply(context, *roles, sep='\n', sort=True)

    @commands.command()
    async def aliases(self, context: Context):
        roles_by_id = {x.id: x for x in context.guild.roles}
        aliases = db.session.query(RoleAlias).filter_by(server_id=context.guild.id)
        await self.reply(
            context,
            *[f'{x.alias} -> {roles_by_id[x.role_id]}' for x in aliases],
            sep='\n',
            sort=True,
        )
