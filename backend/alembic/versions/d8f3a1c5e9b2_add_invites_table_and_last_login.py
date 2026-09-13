"""add invites table and users.last_login_at

Revision ID: d8f3a1c5e9b2
Revises: cd92a81fdacd
Create Date: 2026-09-13 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd8f3a1c5e9b2'
down_revision: Union[str, Sequence[str], None] = 'cd92a81fdacd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))

    op.create_table(
        "invites",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("code", sa.String(length=12), nullable=False),
        sa.Column("teacher_id", sa.Uuid(), nullable=False),
        sa.Column("student_name_hint", sa.String(length=64), nullable=True),
        sa.Column("status", sa.Enum("PENDING", "JOINED", "EXPIRED", name="invitestatus"), nullable=False),
        sa.Column("student_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["teacher_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("invites")
    sa.Enum(name="invitestatus").drop(op.get_bind(), checkfirst=True)
    op.drop_column("users", "last_login_at")
