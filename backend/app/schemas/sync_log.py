from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class SyncRequest(BaseModel):
    """手动触发同步请求"""
    start_time: Optional[str] = Field(None, description="开始时间 (格式: YYYY-MM-DD HH:MM:SS)")
    end_time: Optional[str] = Field(None, description="结束时间 (格式: YYYY-MM-DD HH:MM:SS)")


class SyncResponse(BaseModel):
    """同步响应"""
    status: str
    fetched_count: int
    new_count: int = 0
    updated_count: int = 0
    message: str


class SyncLogResponse(BaseModel):
    """同步日志项"""
    id: int
    sync_type: str  # 'auto' or 'manual'
    status: str  # 'success' or 'error'
    fetched_count: int
    new_count: int
    updated_count: int
    error_message: Optional[str] = None
    start_time: datetime

    class Config:
        from_attributes = True


class SyncLogList(BaseModel):
    """同步日志列表响应"""
    items: List[SyncLogResponse]
    total: int
    page: int
    page_size: int
