"""Add new_count and updated_count to sync_logs

Revision ID: 008
Revises: 007
Create Date: 2025-11-21

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new_count column
    op.add_column(
        'sync_logs',
        sa.Column('new_count', sa.Integer, nullable=True, server_default='0')
    )

    # Add updated_count column
    op.add_column(
        'sync_logs',
        sa.Column('updated_count', sa.Integer, nullable=True, server_default='0')
    )


def downgrade() -> None:
    op.drop_column('sync_logs', 'updated_count')
    op.drop_column('sync_logs', 'new_count')
