from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from app.database import Base


class SyncLog(Base):
    """数据同步日志模型 - 记录每次数据同步操作"""

    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sync_type = Column(String(20), nullable=False)  # 'auto' or 'manual'
    status = Column(String(20), nullable=False)  # 'success', 'failed', 'in_progress'
    start_time = Column(TIMESTAMP, nullable=False, server_default=func.now(), index=True)
    end_time = Column(TIMESTAMP, nullable=True)
    fetched_count = Column(Integer, nullable=True, server_default='0')
    error_message = Column(Text, nullable=True)
    operator = Column(String(100), nullable=True)  # Username who triggered manual sync

    def __repr__(self):
        return (
            f"<SyncLog(id={self.id}, "
            f"sync_type='{self.sync_type}', "
            f"status='{self.status}', "
            f"fetched_count={self.fetched_count})>"
        )
