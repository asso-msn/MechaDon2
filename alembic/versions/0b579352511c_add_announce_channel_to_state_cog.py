"""Add announce channel to state cog

Revision ID: 0b579352511c
Revises: a634d3ec8146
Create Date: 2024-05-15 22:55:36.794539

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b579352511c'
down_revision = 'a634d3ec8146'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('states', schema=None) as batch_op:
        batch_op.add_column(sa.Column('announce_channel_id', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('states', schema=None) as batch_op:
        batch_op.drop_column('announce_channel_id')

    # ### end Alembic commands ###
