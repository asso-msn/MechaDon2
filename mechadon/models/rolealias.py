import sqlalchemy as sa

from mechadon import db


class RoleAlias(db.Base):
    __tablename__ = "role_aliases"

    role_id = sa.Column(db.Id, nullable=False, primary_key=True)
    server_id = sa.Column(db.Id, nullable=False, primary_key=True)
    alias = sa.Column(sa.String, primary_key=True)
    added_by = sa.Column(db.Id)

    def str(self, context):
        roles_by_id = {x.id: x for x in context.guild.roles}
        role = roles_by_id[self.role_id]
        return f"{self.alias} -> {role.name}"
