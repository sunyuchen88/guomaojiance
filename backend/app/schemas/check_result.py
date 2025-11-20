from pydantic import BaseModel, Field
from typing import List, Optional


class CheckItemResult(BaseModel):
    """检测项目结果"""
    check_item_id: int
    check_item_name: str
    result: str = Field(..., description="合格/不合格")
    item_indicator: str = Field(..., description="检测指标值")


class CheckResultInput(BaseModel):
    """检测结果录入请求"""
    check_result: str = Field(..., description="总体检测结果: 合格/不合格")
    check_items: List[CheckItemResult] = Field(..., min_items=1, description="检测项目结果列表")


class CheckResultResponse(BaseModel):
    """检测结果响应"""
    id: int
    status: int
    message: str = "Result saved successfully"
