"""Add joinchan, factorize leave and join channels into doorways

Revision ID: c3f1a9d2b7e5
Revises: 0b579352511c
Create Date: 2026-10-27 12:00:00.000000

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "c3f1a9d2b7e5"
down_revision = "0b579352511c"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "doorways",
        sa.Column("channel_id", sa.Integer(), nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("event", sa.String(), nullable=False),
        sa.Column("added_by", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint(
            "channel_id",
            "server_id",
            "event",
            name=op.f("pk_doorways"),
        ),
    )
    op.execute(
        "INSERT INTO doorways "
        "(channel_id, server_id, event, added_by) "
        "SELECT channel_id, server_id, 'leave', added_by "
        "FROM leave_message_channels"
    )
    op.drop_table("leave_message_channels")


def downgrade():
    op.create_table(
        "leave_message_channels",
        sa.Column("channel_id", sa.Integer(), nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=False),
        sa.Column("added_by", sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint(
            "channel_id",
            "server_id",
            name=op.f("pk_leave_message_channels"),
        ),
    )
    op.execute(
        "INSERT INTO leave_message_channels "
        "(channel_id, server_id, added_by) "
        "SELECT channel_id, server_id, added_by "
        "FROM doorways WHERE event = 'leave'"
    )
    op.drop_table("doorways")
