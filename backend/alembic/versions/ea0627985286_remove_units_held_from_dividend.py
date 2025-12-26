"""remove_units_held_from_dividend

Revision ID: ea0627985286
Revises: 8ad82855479d
Create Date: 2025-12-25 23:56:36.438671

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ea0627985286'
down_revision: Union[str, None] = '8ad82855479d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop check constraint first
    op.drop_constraint('ck_dividend_units', 'dividend', type_='check')

    # Drop units_held column
    op.drop_column('dividend', 'units_held')


def downgrade() -> None:
    # Add units_held column back
    op.add_column('dividend', sa.Column('units_held', sa.Integer(), nullable=False, server_default='1'))

    # Re-add check constraint
    op.create_check_constraint('ck_dividend_units', 'dividend', 'units_held > 0')
