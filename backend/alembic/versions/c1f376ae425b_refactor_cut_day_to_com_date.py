"""refactor_cut_day_to_com_date

Revision ID: c1f376ae425b
Revises: ea0627985286
Create Date: 2025-12-26 10:02:32.269511

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1f376ae425b'
down_revision: Union[str, None] = 'ea0627985286'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Step 1: Add com_date column to dividend table
    op.add_column('dividend', sa.Column('com_date', sa.Date(), nullable=True, comment='Data COM - cut-off date for dividend eligibility'))
    op.create_index('ix_dividend_com_date', 'dividend', ['com_date'], unique=False)

    # Step 2: Migrate existing data - calculate com_date from FII cut_day and payment_date
    op.execute("""
        UPDATE dividend
        SET com_date = (
            SELECT CASE
                WHEN f.cut_day IS NULL THEN NULL
                WHEN f.cut_day <= EXTRACT(DAY FROM (DATE_TRUNC('month', d.payment_date) + INTERVAL '1 month - 1 day')::date)
                    THEN (DATE_TRUNC('month', d.payment_date) + (f.cut_day - 1) * INTERVAL '1 day')::date
                ELSE (DATE_TRUNC('month', d.payment_date) + INTERVAL '1 month - 1 day')::date
            END
            FROM dividend d
            JOIN fii f ON d.fii_pk = f.pk
            WHERE d.pk = dividend.pk
        )
    """)

    # Step 3: Remove cut_day from fii table
    op.drop_index('ix_fii_cut_day', table_name='fii')
    op.drop_column('fii', 'cut_day')


def downgrade() -> None:
    # Step 1: Re-add cut_day to fii table
    op.add_column('fii', sa.Column('cut_day', sa.Integer(), nullable=True, comment='Day of month for dividend cut-off (1-31)'))
    op.create_index('ix_fii_cut_day', 'fii', ['cut_day'], unique=False)

    # Step 2: Best effort - restore cut_day from most common com_date day per FII
    op.execute("""
        UPDATE fii
        SET cut_day = (
            SELECT EXTRACT(DAY FROM com_date)::integer
            FROM dividend
            WHERE dividend.fii_pk = fii.pk AND dividend.com_date IS NOT NULL
            GROUP BY EXTRACT(DAY FROM com_date)
            ORDER BY COUNT(*) DESC
            LIMIT 1
        )
    """)

    # Step 3: Remove com_date from dividend table
    op.drop_index('ix_dividend_com_date', table_name='dividend')
    op.drop_column('dividend', 'com_date')
