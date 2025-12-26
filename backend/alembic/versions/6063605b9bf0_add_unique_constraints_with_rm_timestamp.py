"""add_unique_constraints_with_rm_timestamp

Revision ID: 6063605b9bf0
Revises: 001
Create Date: 2025-12-25 16:13:58.480379

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6063605b9bf0'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old unique constraints
    op.drop_constraint('uq_fii_tag', 'fii', type_='unique')
    op.drop_constraint('uq_user_email', 'user', type_='unique')
    op.drop_constraint('uq_user_username', 'user', type_='unique')
    op.drop_constraint('uq_role_name', 'role', type_='unique')
    op.drop_constraint('uq_permission_resource_action', 'permission', type_='unique')

    # Add new unique constraints that include rm_timestamp
    op.create_unique_constraint('uq_fii_tag_rm_timestamp', 'fii', ['tag', 'rm_timestamp'])
    op.create_unique_constraint('uq_user_username_rm_timestamp', 'user', ['username', 'rm_timestamp'])
    op.create_unique_constraint('uq_user_email_rm_timestamp', 'user', ['email', 'rm_timestamp'])
    op.create_unique_constraint('uq_role_name_rm_timestamp', 'role', ['name', 'rm_timestamp'])
    op.create_unique_constraint('uq_role_description_rm_timestamp', 'role', ['description', 'rm_timestamp'])
    op.create_unique_constraint('uq_permission_resource_action_rm_timestamp', 'permission', ['resource', 'action', 'rm_timestamp'])
    op.create_unique_constraint('uq_permission_description_rm_timestamp', 'permission', ['description', 'rm_timestamp'])


def downgrade() -> None:
    # Drop new unique constraints
    op.drop_constraint('uq_fii_tag_rm_timestamp', 'fii', type_='unique')
    op.drop_constraint('uq_user_username_rm_timestamp', 'user', type_='unique')
    op.drop_constraint('uq_user_email_rm_timestamp', 'user', type_='unique')
    op.drop_constraint('uq_role_name_rm_timestamp', 'role', type_='unique')
    op.drop_constraint('uq_role_description_rm_timestamp', 'role', type_='unique')
    op.drop_constraint('uq_permission_resource_action_rm_timestamp', 'permission', type_='unique')
    op.drop_constraint('uq_permission_description_rm_timestamp', 'permission', type_='unique')

    # Restore old unique constraints
    op.create_unique_constraint('uq_fii_tag', 'fii', ['tag'])
    op.create_unique_constraint('uq_user_email', 'user', ['email'])
    op.create_unique_constraint('uq_user_username', 'user', ['username'])
    op.create_unique_constraint('uq_role_name', 'role', ['name'])
    op.create_unique_constraint('uq_permission_resource_action', 'permission', ['resource', 'action'])
