"""add teacher role and group teacher_id

Revision ID: 1c885de625a8
Revises: 3246589a9115
Create Date: 2026-09-13 11:32:14.803359

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c885de625a8'
down_revision: Union[str, Sequence[str], None] = '3246589a9115'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ALTER TYPE ... ADD VALUE cannot run inside a normal transaction block.
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE role ADD VALUE IF NOT EXISTS 'TEACHER'")

    op.add_column("groups", sa.Column("teacher_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_groups_teacher_id_users", "groups", "users", ["teacher_id"], ["id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("fk_groups_teacher_id_users", "groups", type_="foreignkey")
    op.drop_column("groups", "teacher_id")
    # Postgres has no DROP VALUE for enums (would require recreating the type
    # and rewriting every dependent column) - 'TEACHER' intentionally stays in
    # the `role` enum type on downgrade. Harmless: no row can reference it
    # unless a TEACHER user was created after this migration ran.
