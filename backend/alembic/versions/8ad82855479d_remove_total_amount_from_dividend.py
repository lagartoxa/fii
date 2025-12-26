"""remove_total_amount_from_dividend

Revision ID: 8ad82855479d
Revises: c8a40ca433ec
Create Date: 2025-12-25 23:12:30.120822

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ad82855479d'
down_revision: Union[str, None] = 'c8a40ca433ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove total_amount column from dividend table
    op.drop_column('dividend', 'total_amount')


def downgrade() -> None:
    # Add total_amount column back
    op.add_column('dividend', sa.Column('total_amount', sa.Numeric(precision=10, scale=2), nullable=False, server_default='0'))
