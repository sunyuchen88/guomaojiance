"""Create system_config table

Revision ID: 006
Revises: 005
Create Date: 2025-11-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'system_config',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('api_base_url', sa.String(500), nullable=False),
        sa.Column('client_app_id', sa.String(100), nullable=False),
        sa.Column('client_secret', sa.String(255), nullable=False),
        sa.Column('sync_interval_minutes', sa.Integer, nullable=True, server_default='30'),
        sa.Column('file_storage_path', sa.String(500), nullable=True, server_default="'/uploads/reports'"),
        sa.Column('server_domain', sa.String(200), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=func.now(), onupdate=func.now()),
        sa.CheckConstraint('id = 1', name='single_row_constraint'),
    )


def downgrade() -> None:
    op.drop_table('system_config')
