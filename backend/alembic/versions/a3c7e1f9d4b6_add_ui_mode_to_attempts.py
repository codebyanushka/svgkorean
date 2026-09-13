"""add ui_mode to attempts

Revision ID: a3c7e1f9d4b6
Revises: f2b6c7d8e9a1
Create Date: 2026-09-13 19:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a3c7e1f9d4b6'
down_revision: Union[str, Sequence[str], None] = 'f2b6c7d8e9a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("attempts", sa.Column("ui_mode", sa.String(length=32), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("attempts", "ui_mode")
