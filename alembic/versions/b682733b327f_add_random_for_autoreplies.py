"""Add random for autoreplies

Revision ID: b682733b327f
Revises: 44f08398ec4f
Create Date: 2022-12-14 10:13:12.343921

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b682733b327f'
down_revision = '44f08398ec4f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('autoreplies', schema=None) as batch_op:
        batch_op.add_column(sa.Column('random', sa.Integer(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('autoreplies', schema=None) as batch_op:
        batch_op.drop_column('random')

    # ### end Alembic commands ###
