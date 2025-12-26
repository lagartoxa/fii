"""add_cut_day_to_fii

Revision ID: c8a40ca433ec
Revises: 6063605b9bf0
Create Date: 2025-12-25 22:42:15.400410

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8a40ca433ec'
down_revision: Union[str, None] = '6063605b9bf0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add cut_day column to fii table as integer (1-31)
    op.add_column('fii', sa.Column('cut_day', sa.Integer(), nullable=True, comment='Day of month for dividend cut-off (1-31)'))

    # Create index on cut_day for query performance
    op.create_index('ix_fii_cut_day', 'fii', ['cut_day'], unique=False)


def downgrade() -> None:
    # Drop index first
    op.drop_index('ix_fii_cut_day', table_name='fii')

    # Drop cut_day column
    op.drop_column('fii', 'cut_day')
