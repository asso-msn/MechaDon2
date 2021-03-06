"""Add leavechan

Revision ID: ee5fa059dbc1
Revises: abe0e2d9cc02
Create Date: 2021-12-03 18:29:47.933818

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee5fa059dbc1'
down_revision = 'abe0e2d9cc02'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('leave_message_channels',
    sa.Column('channel_id', sa.Integer(), nullable=False),
    sa.Column('server_id', sa.Integer(), nullable=False),
    sa.Column('added_by', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('channel_id', 'server_id', name=op.f('pk_leave_message_channels'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('leave_message_channels')
    # ### end Alembic commands ###
