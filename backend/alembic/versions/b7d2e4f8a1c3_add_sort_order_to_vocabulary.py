"""add sort_order to vocabulary

Revision ID: b7d2e4f8a1c3
Revises: a3c7e1f9d4b6
Create Date: 2026-09-14 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b7d2e4f8a1c3'
down_revision: Union[str, Sequence[str], None] = 'a3c7e1f9d4b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("vocabulary", sa.Column("sort_order", sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("vocabulary", "sort_order")
