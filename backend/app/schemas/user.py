from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserLogin(BaseModel):
    """用户登录请求模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=8, description="密码")


class UserBase(BaseModel):
    """用户基础信息"""
    username: str
    name: str
    role: str


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT令牌响应模型"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
