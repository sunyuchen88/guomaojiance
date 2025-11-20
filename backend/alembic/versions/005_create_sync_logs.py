"""Create sync_logs table

Revision ID: 005
Revises: 004
Create Date: 2025-11-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'sync_logs',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('sync_type', sa.String(20), nullable=False),  # 'auto' or 'manual'
        sa.Column('status', sa.String(20), nullable=False),  # 'success', 'failed', 'in_progress'
        sa.Column('start_time', sa.TIMESTAMP, nullable=False, server_default=func.now()),
        sa.Column('end_time', sa.TIMESTAMP, nullable=True),
        sa.Column('fetched_count', sa.Integer, nullable=True, server_default='0'),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('operator', sa.String(100), nullable=True),  # Username who triggered manual sync
    )

    # Create index for time-based queries
    op.create_index('idx_sync_logs_start_time', 'sync_logs', [sa.text('start_time DESC')])


def downgrade() -> None:
    op.drop_index('idx_sync_logs_start_time', table_name='sync_logs')
    op.drop_table('sync_logs')
