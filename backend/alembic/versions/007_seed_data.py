"""Seed initial data

Revision ID: 007
Revises: 006
Create Date: 2025-11-19

"""
from alembic import op
import sqlalchemy as sa
from passlib.context import CryptContext

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def upgrade() -> None:
    # Insert default admin user
    # Password: admin123
    hashed_password = pwd_context.hash("admin123")

    op.execute(
        sa.text("""
            INSERT INTO users (username, password_hash, name, role, created_at)
            VALUES (:username, :password_hash, :name, :role, NOW())
        """).bindparams(
            username="admin",
            password_hash=hashed_password,
            name="管理员",
            role="admin"
        )
    )

    # Insert default system configuration
    op.execute(
        sa.text("""
            INSERT INTO system_config (
                id,
                api_base_url,
                client_app_id,
                client_secret,
                sync_interval_minutes,
                file_storage_path,
                server_domain,
                updated_at
            )
            VALUES (
                1,
                :api_base_url,
                :client_app_id,
                :client_secret,
                30,
                '/uploads/reports',
                :server_domain,
                NOW()
            )
        """).bindparams(
            api_base_url="https://test1.yunxianpei.com",
            client_app_id="689_abc",
            client_secret="67868790",
            server_domain="http://localhost:8000"
        )
    )


def downgrade() -> None:
    # Delete seed data
    op.execute("DELETE FROM system_config WHERE id = 1")
    op.execute("DELETE FROM users WHERE username = 'admin'")
