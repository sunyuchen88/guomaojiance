"""Create check_object_items table

Revision ID: 003
Revises: 002
Create Date: 2025-11-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'check_object_items',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('check_object_item_id', sa.BigInteger, unique=True, nullable=False),
        sa.Column('check_object_id', sa.BigInteger, nullable=False),
        sa.Column('check_item_id', sa.Integer, nullable=False),
        sa.Column('check_item_name', sa.String(200), nullable=False),
        sa.Column('num', sa.String(50), nullable=True),
        sa.Column('result', sa.String(20), nullable=True),
        sa.Column('check_time', sa.TIMESTAMP, nullable=True),
        sa.Column('check_admin', sa.String(100), nullable=True),
        sa.Column('status', sa.SmallInteger, nullable=True, server_default='1'),
        sa.Column('create_time', sa.TIMESTAMP, server_default=func.now()),
        sa.Column('reference_value', sa.String(100), nullable=True),
        sa.Column('item_indicator', sa.String(200), nullable=True),
    )

    # Create index for check_object_id foreign key lookups
    op.create_index('idx_check_object_items_check_object_id', 'check_object_items', ['check_object_id'])

    # Create foreign key constraint
    op.create_foreign_key(
        'fk_check_object_items_check_object',
        'check_object_items', 'check_objects',
        ['check_object_id'], ['check_object_id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_constraint('fk_check_object_items_check_object', 'check_object_items', type_='foreignkey')
    op.drop_index('idx_check_object_items_check_object_id', table_name='check_object_items')
    op.drop_table('check_object_items')
