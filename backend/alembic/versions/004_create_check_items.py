"""Create check_items table

Revision ID: 004
Revises: 003
Create Date: 2025-11-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'check_items',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('item_id', sa.Integer, unique=True, nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('method_id', sa.Integer, nullable=True),
        sa.Column('method_name', sa.String(200), nullable=True),
        sa.Column('basic_id', sa.Integer, nullable=True),
        sa.Column('basic_name', sa.String(500), nullable=True),
        sa.Column('indicators_id', sa.Integer, nullable=True),
        sa.Column('indicators_name', sa.String(200), nullable=True),
        sa.Column('reference_values', sa.String(100), nullable=True),
        sa.Column('fee', sa.Numeric(10, 2), nullable=True, server_default='0.01'),
        sa.Column('created_at', sa.TIMESTAMP, server_default=func.now()),
    )

    # Create indexes
    op.create_index('idx_check_items_item_id', 'check_items', ['item_id'])
    op.create_index('idx_check_items_name', 'check_items', ['name'])


def downgrade() -> None:
    op.drop_index('idx_check_items_name', table_name='check_items')
    op.drop_index('idx_check_items_item_id', table_name='check_items')
    op.drop_table('check_items')
