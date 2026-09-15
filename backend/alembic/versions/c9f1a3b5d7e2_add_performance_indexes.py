"""add performance indexes on hot foreign-key columns

Revision ID: c9f1a3b5d7e2
Revises: b7d2e4f8a1c3
Create Date: 2026-09-15 06:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c9f1a3b5d7e2'
down_revision: Union[str, Sequence[str], None] = 'b7d2e4f8a1c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    attempts/mistakes grow unbounded (every practice submission, forever)
    and every teacher dashboard/analytics query filters by user_id - without
    an index these become full table scans as usage grows. group_members is
    queried by group_id (a teacher's whole class) just as often.
    """
    op.create_index("ix_attempts_user_id", "attempts", ["user_id"])
    op.create_index("ix_mistakes_user_id", "mistakes", ["user_id"])
    op.create_index("ix_group_members_group_id", "group_members", ["group_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_group_members_group_id", table_name="group_members")
    op.drop_index("ix_mistakes_user_id", table_name="mistakes")
    op.drop_index("ix_attempts_user_id", table_name="attempts")
