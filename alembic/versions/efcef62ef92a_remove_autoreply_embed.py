"""Remove autoreply embed

Revision ID: efcef62ef92a
Revises: aca8f7a94bcc
Create Date: 2024-05-15 03:20:20.283906

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "efcef62ef92a"
down_revision = "aca8f7a94bcc"
branch_labels = None
depends_on = None


def upgrade():
    # get all row in table "autoreplies" with a value in the column "file_url"
    table = sa.sql.table(
        "autoreplies",
        sa.Column("trigger", sa.String),
        sa.Column("text", sa.String),
        sa.Column("file_url", sa.String),
    )
    conn = op.get_bind()
    rows = conn.execute(table.select()).fetchall()
    for row in rows:
        if not row.file_url:
            continue
        conn.execute(
            table.update()
            .where(table.c.file_url == row.file_url)
            .values(text=row.file_url)
        )
        print(f"Migrated reply {row.trigger} from file_url to text")

    with op.batch_alter_table("autoreplies", schema=None) as batch_op:
        batch_op.drop_column("file_url")


def downgrade():
    with op.batch_alter_table("autoreplies", schema=None) as batch_op:
        batch_op.add_column(sa.Column("file_url", sa.String))
