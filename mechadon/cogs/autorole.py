from discord import Member
import sqlalchemy as sa

from mechadon import db
from mechadon.converters import RoleLenient
from . import BaseCog, Cog, Context, commands


class Autorole(db.Base):
    role_id = sa.Column(db.Id, nullable=False, primary_key=True)
    server_id = sa.Column(db.Id, nullable=False, primary_key=True)
    added_by = sa.Column(db.Id)

    def __init__(self, *args, **kwargs):
        if (role := kwargs.pop('role')):
            kwargs['role_id'] = role.id
            kwargs['server_id'] = role.guild.id
        super().__init__(*args, **kwargs)


class AutoroleCog(BaseCog):
    @staticmethod
    def get_autoroles(guild):
        return db.session.query(Autorole).filter_by(server_id=guild.id)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def autorole(self, context: Context, *, role: RoleLenient):
        autorole_db = db.session.get(Autorole, (role.id, role.guild.id))
        if autorole_db:
            db.session.delete(autorole_db)
            action = 'Removed'
        else:
            autorole_db = Autorole(role=role, added_by=context.author.id)
            db.session.add(autorole_db)
            action = 'Added'
        db.session.commit()
        await self.reply(context, action, autorole_db)

    @commands.command()
    async def autoroles(self, context: Context):
        roles_by_id = self.get_roles_by_id(context)
        autoroles = [
            roles_by_id[x.role_id] for x in self.get_autoroles(context.guild)
        ]
        await self.reply(context, *autoroles, sep='\n')

    @Cog.listener()
    async def on_member_join(self, member: Member):
        autoroles = self.get_autoroles(member.guild)
        if autoroles:
            await member.add_roles(*autoroles)
