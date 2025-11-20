from sqlalchemy import Column, Integer, String, TIMESTAMP, CheckConstraint
from sqlalchemy.sql import func
from app.database import Base


class SystemConfig(Base):
    """系统配置模型 - 存储系统配置信息(单行表)"""

    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True)  # Always 1
    api_base_url = Column(String(500), nullable=False)
    client_app_id = Column(String(100), nullable=False)
    client_secret = Column(String(255), nullable=False)
    sync_interval_minutes = Column(Integer, nullable=True, server_default='30')
    file_storage_path = Column(String(500), nullable=True, server_default="'/uploads/reports'")
    server_domain = Column(String(200), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint('id = 1', name='single_row_constraint'),
    )

    def __repr__(self):
        return (
            f"<SystemConfig(api_base_url='{self.api_base_url}', "
            f"sync_interval={self.sync_interval_minutes} minutes)>"
        )
