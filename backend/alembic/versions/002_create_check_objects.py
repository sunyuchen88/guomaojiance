"""Create check_objects table

Revision ID: 002
Revises: 001
Create Date: 2025-11-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'check_objects',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('check_object_id', sa.BigInteger, unique=True, nullable=False),
        sa.Column('day_num', sa.String(10), nullable=True),
        sa.Column('check_object_union_num', sa.String(50), nullable=False),
        sa.Column('code_url', sa.Text, nullable=True),
        sa.Column('submission_goods_id', sa.Integer, nullable=True),
        sa.Column('submission_goods_name', sa.String(200), nullable=True),
        sa.Column('submission_goods_area', sa.String(100), nullable=True),
        sa.Column('submission_goods_location', sa.String(200), nullable=True),
        sa.Column('submission_goods_unit', sa.String(20), nullable=True),
        sa.Column('submission_goods_car_number', sa.String(20), nullable=True),
        sa.Column('submission_method', sa.String(50), nullable=True),
        sa.Column('submission_person', sa.String(100), nullable=True),
        sa.Column('submission_person_mobile', sa.String(20), nullable=True),
        sa.Column('submission_person_company', sa.String(200), nullable=True),
        sa.Column('driver', sa.String(100), nullable=True),
        sa.Column('driver_mobile', sa.String(20), nullable=True),
        sa.Column('check_type', sa.String(50), nullable=True),
        sa.Column('status', sa.SmallInteger, nullable=False, server_default='0'),
        sa.Column('is_receive', sa.SmallInteger, nullable=True, server_default='1'),
        sa.Column('check_start_time', sa.TIMESTAMP, nullable=True),
        sa.Column('check_end_time', sa.TIMESTAMP, nullable=True),
        sa.Column('check_result', sa.String(20), nullable=True),
        sa.Column('check_result_url', sa.Text, nullable=True),
        sa.Column('create_admin', sa.String(100), nullable=True),
        sa.Column('create_time', sa.TIMESTAMP, server_default=func.now()),
        sa.Column('synced_at', sa.TIMESTAMP, server_default=func.now()),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=func.now(), onupdate=func.now()),
    )

    # Create indexes for common query patterns
    op.create_index('idx_check_objects_status', 'check_objects', ['status'])
    op.create_index('idx_check_objects_union_num', 'check_objects', ['check_object_union_num'])
    op.create_index('idx_check_objects_company', 'check_objects', ['submission_person_company'])
    op.create_index('idx_check_objects_check_start_time', 'check_objects', ['check_start_time'])
    op.create_index('idx_check_objects_check_object_id', 'check_objects', ['check_object_id'])


def downgrade() -> None:
    op.drop_index('idx_check_objects_check_object_id', table_name='check_objects')
    op.drop_index('idx_check_objects_check_start_time', table_name='check_objects')
    op.drop_index('idx_check_objects_company', table_name='check_objects')
    op.drop_index('idx_check_objects_union_num', table_name='check_objects')
    op.drop_index('idx_check_objects_status', table_name='check_objects')
    op.drop_table('check_objects')
