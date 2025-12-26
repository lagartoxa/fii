"""Initial schema with simplified models

Revision ID: 001
Revises:
Create Date: 2024-12-24 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create update_updated_at_column function for triggers
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    # ========================================================================
    # TABLE 1: user
    # ========================================================================
    op.create_table(
        'user',
        sa.Column('pk', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('rm_timestamp', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_by_pk', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_by_pk', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('pk'),
        sa.UniqueConstraint('email', name='uq_user_email'),
        sa.UniqueConstraint('username', name='uq_user_username'),
        sa.ForeignKeyConstraint(['created_by_pk'], ['user.pk'], name='fk_user_created_by', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by_pk'], ['user.pk'], name='fk_user_updated_by', ondelete='SET NULL'),
    )
    op.create_index('idx_user_email', 'user', ['email'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.create_index('idx_user_username', 'user', ['username'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.create_index('idx_user_is_active', 'user', ['is_active'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.execute("CREATE TRIGGER update_user_updated_at BEFORE UPDATE ON \"user\" FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")

    # ========================================================================
    # TABLE 2: role
    # ========================================================================
    op.create_table(
        'role',
        sa.Column('pk', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('rm_timestamp', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_by_pk', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_by_pk', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('pk'),
        sa.UniqueConstraint('name', name='uq_role_name'),
        sa.ForeignKeyConstraint(['created_by_pk'], ['user.pk'], name='fk_role_created_by', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by_pk'], ['user.pk'], name='fk_role_updated_by', ondelete='SET NULL'),
    )
    op.create_index('idx_role_name', 'role', ['name'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.execute("CREATE TRIGGER update_role_updated_at BEFORE UPDATE ON role FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")

    # ========================================================================
    # TABLE 3: permission
    # ========================================================================
    op.create_table(
        'permission',
        sa.Column('pk', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('resource', sa.String(length=100), nullable=False),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('rm_timestamp', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_by_pk', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_by_pk', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('pk'),
        sa.UniqueConstraint('resource', 'action', name='uq_permission_resource_action'),
        sa.ForeignKeyConstraint(['created_by_pk'], ['user.pk'], name='fk_permission_created_by', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by_pk'], ['user.pk'], name='fk_permission_updated_by', ondelete='SET NULL'),
    )
    op.create_index('idx_permission_resource', 'permission', ['resource'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.create_index('idx_permission_action', 'permission', ['action'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.execute("CREATE TRIGGER update_permission_updated_at BEFORE UPDATE ON permission FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")

    # ========================================================================
    # TABLE 4: user_role
    # ========================================================================
    op.create_table(
        'user_role',
        sa.Column('pk', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('user_pk', sa.BigInteger(), nullable=False),
        sa.Column('role_pk', sa.BigInteger(), nullable=False),
        sa.Column('rm_timestamp', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_by_pk', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_by_pk', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('pk'),
        sa.UniqueConstraint('user_pk', 'role_pk', name='uq_user_role_user_role'),
        sa.ForeignKeyConstraint(['user_pk'], ['user.pk'], name='fk_user_role_user', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_pk'], ['role.pk'], name='fk_user_role_role', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_pk'], ['user.pk'], name='fk_user_role_created_by', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by_pk'], ['user.pk'], name='fk_user_role_updated_by', ondelete='SET NULL'),
    )
    op.create_index('idx_user_role_user_pk', 'user_role', ['user_pk'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.create_index('idx_user_role_role_pk', 'user_role', ['role_pk'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.execute("CREATE TRIGGER update_user_role_updated_at BEFORE UPDATE ON user_role FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")

    # ========================================================================
    # TABLE 5: role_permission
    # ========================================================================
    op.create_table(
        'role_permission',
        sa.Column('pk', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('role_pk', sa.BigInteger(), nullable=False),
        sa.Column('permission_pk', sa.BigInteger(), nullable=False),
        sa.Column('rm_timestamp', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_by_pk', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_by_pk', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('pk'),
        sa.UniqueConstraint('role_pk', 'permission_pk', name='uq_role_permission_role_permission'),
        sa.ForeignKeyConstraint(['role_pk'], ['role.pk'], name='fk_role_permission_role', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_pk'], ['permission.pk'], name='fk_role_permission_permission', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_pk'], ['user.pk'], name='fk_role_permission_created_by', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by_pk'], ['user.pk'], name='fk_role_permission_updated_by', ondelete='SET NULL'),
    )
    op.create_index('idx_role_permission_role_pk', 'role_permission', ['role_pk'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.create_index('idx_role_permission_permission_pk', 'role_permission', ['permission_pk'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.execute("CREATE TRIGGER update_role_permission_updated_at BEFORE UPDATE ON role_permission FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")

    # ========================================================================
    # TABLE 6: fii
    # ========================================================================
    op.create_table(
        'fii',
        sa.Column('pk', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('tag', sa.String(length=20), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('sector', sa.String(length=100), nullable=True),
        sa.Column('rm_timestamp', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_by_pk', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_by_pk', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('pk'),
        sa.UniqueConstraint('tag', name='uq_fii_tag'),
        sa.ForeignKeyConstraint(['created_by_pk'], ['user.pk'], name='fk_fii_created_by', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by_pk'], ['user.pk'], name='fk_fii_updated_by', ondelete='SET NULL'),
    )
    op.create_index('idx_fii_tag', 'fii', ['tag'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.create_index('idx_fii_sector', 'fii', ['sector'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.execute("CREATE TRIGGER update_fii_updated_at BEFORE UPDATE ON fii FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")

    # ========================================================================
    # TABLE 7: fii_transaction
    # ========================================================================
    op.create_table(
        'fii_transaction',
        sa.Column('pk', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('user_pk', sa.BigInteger(), nullable=False),
        sa.Column('fii_pk', sa.BigInteger(), nullable=False),
        sa.Column('transaction_type', sa.String(length=10), nullable=False),
        sa.Column('transaction_date', sa.Date(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('price_per_unit', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('rm_timestamp', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_by_pk', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_by_pk', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('pk'),
        sa.ForeignKeyConstraint(['user_pk'], ['user.pk'], name='fk_fii_transaction_user', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['fii_pk'], ['fii.pk'], name='fk_fii_transaction_fii', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by_pk'], ['user.pk'], name='fk_fii_transaction_created_by', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by_pk'], ['user.pk'], name='fk_fii_transaction_updated_by', ondelete='SET NULL'),
        sa.CheckConstraint('transaction_type IN (\'buy\', \'sell\')', name='ck_fii_transaction_type'),
        sa.CheckConstraint('quantity > 0', name='ck_fii_transaction_quantity'),
        sa.CheckConstraint('price_per_unit > 0', name='ck_fii_transaction_price'),
        sa.CheckConstraint('total_amount > 0', name='ck_fii_transaction_total'),
    )
    op.create_index('idx_fii_transaction_user_pk', 'fii_transaction', ['user_pk'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.create_index('idx_fii_transaction_fii_pk', 'fii_transaction', ['fii_pk'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.create_index('idx_fii_transaction_date', 'fii_transaction', ['transaction_date'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.create_index('idx_fii_transaction_type', 'fii_transaction', ['transaction_type'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.execute("CREATE TRIGGER update_fii_transaction_updated_at BEFORE UPDATE ON fii_transaction FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")

    # RLS for fii_transaction
    op.execute("ALTER TABLE fii_transaction ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY user_own_transactions ON fii_transaction
        FOR ALL
        USING (
            user_pk = current_setting('app.current_user_pk', true)::BIGINT OR
            current_setting('app.is_superuser', true)::BOOLEAN = TRUE
        )
    """)

    # ========================================================================
    # TABLE 8: dividend
    # ========================================================================
    op.create_table(
        'dividend',
        sa.Column('pk', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('user_pk', sa.BigInteger(), nullable=False),
        sa.Column('fii_pk', sa.BigInteger(), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('reference_date', sa.Date(), nullable=True),
        sa.Column('amount_per_unit', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('units_held', sa.Integer(), nullable=False),
        sa.Column('total_amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('rm_timestamp', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_by_pk', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_by_pk', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('pk'),
        sa.ForeignKeyConstraint(['user_pk'], ['user.pk'], name='fk_dividend_user', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['fii_pk'], ['fii.pk'], name='fk_dividend_fii', ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['created_by_pk'], ['user.pk'], name='fk_dividend_created_by', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by_pk'], ['user.pk'], name='fk_dividend_updated_by', ondelete='SET NULL'),
        sa.CheckConstraint('amount_per_unit > 0', name='ck_dividend_amount_per_unit'),
        sa.CheckConstraint('units_held > 0', name='ck_dividend_units'),
        sa.CheckConstraint('total_amount > 0', name='ck_dividend_total'),
    )
    op.create_index('idx_dividend_user_pk', 'dividend', ['user_pk'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.create_index('idx_dividend_fii_pk', 'dividend', ['fii_pk'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.create_index('idx_dividend_payment_date', 'dividend', ['payment_date'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.execute("CREATE TRIGGER update_dividend_updated_at BEFORE UPDATE ON dividend FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")

    # RLS for dividend
    op.execute("ALTER TABLE dividend ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY user_own_dividends ON dividend
        FOR ALL
        USING (
            user_pk = current_setting('app.current_user_pk', true)::BIGINT OR
            current_setting('app.is_superuser', true)::BOOLEAN = TRUE
        )
    """)

    # ========================================================================
    # TABLE 9: fii_holding
    # ========================================================================
    op.create_table(
        'fii_holding',
        sa.Column('pk', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('user_pk', sa.BigInteger(), nullable=False),
        sa.Column('fii_pk', sa.BigInteger(), nullable=False),
        sa.Column('total_quantity', sa.Integer(), nullable=False),
        sa.Column('average_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('total_invested', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('current_value', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('total_dividends', sa.Numeric(precision=12, scale=2), nullable=False, server_default='0.00'),
        sa.Column('last_calculated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('rm_timestamp', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_by_pk', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_by_pk', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('pk'),
        sa.UniqueConstraint('user_pk', 'fii_pk', name='uq_fii_holding_user_fii'),
        sa.ForeignKeyConstraint(['user_pk'], ['user.pk'], name='fk_fii_holding_user', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['fii_pk'], ['fii.pk'], name='fk_fii_holding_fii', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_pk'], ['user.pk'], name='fk_fii_holding_created_by', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by_pk'], ['user.pk'], name='fk_fii_holding_updated_by', ondelete='SET NULL'),
        sa.CheckConstraint('total_quantity >= 0', name='ck_fii_holding_quantity'),
        sa.CheckConstraint('average_price >= 0', name='ck_fii_holding_price'),
        sa.CheckConstraint('total_invested >= 0', name='ck_fii_holding_invested'),
    )
    op.create_index('idx_fii_holding_user_pk', 'fii_holding', ['user_pk'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.create_index('idx_fii_holding_fii_pk', 'fii_holding', ['fii_pk'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.execute("CREATE TRIGGER update_fii_holding_updated_at BEFORE UPDATE ON fii_holding FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")

    # RLS for fii_holding
    op.execute("ALTER TABLE fii_holding ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY user_own_holdings ON fii_holding
        FOR ALL
        USING (
            user_pk = current_setting('app.current_user_pk', true)::BIGINT OR
            current_setting('app.is_superuser', true)::BOOLEAN = TRUE
        )
    """)

    # ========================================================================
    # TABLE 10: import_job
    # ========================================================================
    op.create_table(
        'import_job',
        sa.Column('pk', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('user_pk', sa.BigInteger(), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_size', sa.BigInteger(), nullable=False),
        sa.Column('import_type', sa.String(length=50), nullable=False),
        sa.Column('error_details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('rm_timestamp', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_by_pk', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_by_pk', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('pk'),
        sa.ForeignKeyConstraint(['user_pk'], ['user.pk'], name='fk_import_job_user', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_pk'], ['user.pk'], name='fk_import_job_created_by', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by_pk'], ['user.pk'], name='fk_import_job_updated_by', ondelete='SET NULL'),
        sa.CheckConstraint('import_type IN (\'transaction\', \'dividend\')', name='ck_import_job_type'),
    )
    op.create_index('idx_import_job_user_pk', 'import_job', ['user_pk'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.execute("CREATE TRIGGER update_import_job_updated_at BEFORE UPDATE ON import_job FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")

    # RLS for import_job
    op.execute("ALTER TABLE import_job ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY user_own_import_jobs ON import_job
        FOR ALL
        USING (
            user_pk = current_setting('app.current_user_pk', true)::BIGINT OR
            current_setting('app.is_superuser', true)::BOOLEAN = TRUE
        )
    """)

    # ========================================================================
    # TABLE 11: refresh_token
    # ========================================================================
    op.create_table(
        'refresh_token',
        sa.Column('pk', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('user_pk', sa.BigInteger(), nullable=False),
        sa.Column('token', sa.String(length=500), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('device_info', sa.String(length=255), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('rm_timestamp', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_by_pk', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_by_pk', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('pk'),
        sa.UniqueConstraint('token', name='uq_refresh_token_token'),
        sa.ForeignKeyConstraint(['user_pk'], ['user.pk'], name='fk_refresh_token_user', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_pk'], ['user.pk'], name='fk_refresh_token_created_by', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by_pk'], ['user.pk'], name='fk_refresh_token_updated_by', ondelete='SET NULL'),
    )
    op.create_index('idx_refresh_token_user_pk', 'refresh_token', ['user_pk'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.create_index('idx_refresh_token_token', 'refresh_token', ['token'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.create_index('idx_refresh_token_expires_at', 'refresh_token', ['expires_at'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.execute("CREATE TRIGGER update_refresh_token_updated_at BEFORE UPDATE ON refresh_token FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")

    # RLS for refresh_token
    op.execute("ALTER TABLE refresh_token ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY user_own_refresh_tokens ON refresh_token
        FOR ALL
        USING (
            user_pk = current_setting('app.current_user_pk', true)::BIGINT OR
            current_setting('app.is_superuser', true)::BOOLEAN = TRUE
        )
    """)

    # ========================================================================
    # TABLE 12: log
    # ========================================================================
    op.create_table(
        'log',
        sa.Column('pk', sa.BigInteger(), nullable=False, autoincrement=True),
        sa.Column('user_pk', sa.BigInteger(), nullable=True),
        sa.Column('level', sa.String(length=20), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=True),
        sa.Column('resource_pk', sa.BigInteger(), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('details', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('rm_timestamp', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_by_pk', sa.BigInteger(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_by_pk', sa.BigInteger(), nullable=True),
        sa.PrimaryKeyConstraint('pk'),
        sa.ForeignKeyConstraint(['user_pk'], ['user.pk'], name='fk_log_user', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by_pk'], ['user.pk'], name='fk_log_created_by', ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['updated_by_pk'], ['user.pk'], name='fk_log_updated_by', ondelete='SET NULL'),
        sa.CheckConstraint('level IN (\'debug\', \'info\', \'warning\', \'error\', \'critical\')', name='ck_log_level'),
    )
    op.create_index('idx_log_user_pk', 'log', ['user_pk'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.create_index('idx_log_level', 'log', ['level'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.create_index('idx_log_action', 'log', ['action'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.create_index('idx_log_created_at', 'log', ['created_at'], unique=False, postgresql_where=sa.text('rm_timestamp IS NULL'))
    op.execute("CREATE TRIGGER update_log_updated_at BEFORE UPDATE ON log FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();")

    # RLS for log (read-only)
    op.execute("ALTER TABLE log ENABLE ROW LEVEL SECURITY")
    op.execute("""
        CREATE POLICY user_read_own_logs ON log
        FOR SELECT
        USING (
            user_pk = current_setting('app.current_user_pk', true)::BIGINT OR
            current_setting('app.is_superuser', true)::BOOLEAN = TRUE
        )
    """)


def downgrade() -> None:
    op.drop_table('log')
    op.drop_table('refresh_token')
    op.drop_table('import_job')
    op.drop_table('fii_holding')
    op.drop_table('dividend')
    op.drop_table('fii_transaction')
    op.drop_table('fii')
    op.drop_table('role_permission')
    op.drop_table('user_role')
    op.drop_table('permission')
    op.drop_table('role')
    op.drop_table('user')
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
