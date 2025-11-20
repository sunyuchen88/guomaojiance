"""Create users table

Revision ID: 001
Revises:
Create Date: 2025-11-19

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=func.now(), nullable=False),
        sa.Column('last_login_at', sa.TIMESTAMP, nullable=True),
    )

    # Create index on username for login queries
    op.create_index('idx_users_username', 'users', ['username'])


def downgrade() -> None:
    op.drop_index('idx_users_username', table_name='users')
    op.drop_table('users')
