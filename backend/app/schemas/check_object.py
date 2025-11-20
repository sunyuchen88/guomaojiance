from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class CheckObjectItemResponse(BaseModel):
    """检测项目信息响应 - T2.2: 5个核心字段"""
    id: int
    check_item_name: Optional[str] = None  # 1. 检测项目
    check_method: Optional[str] = None     # 2. 检测方法
    unit: Optional[str] = None             # 3. 单位
    num: Optional[str] = None              # 4. 检测结果
    detection_limit: Optional[str] = None  # 5. 检出限
    result: Optional[str] = None           # 结果判定(合格/不合格)
    reference_value: Optional[str] = None  # 参考值
    item_indicator: Optional[str] = None   # 指标

    class Config:
        from_attributes = True


class CheckObjectItemUpdate(BaseModel):
    """更新检测项目 - T2.2: 支持5个核心字段"""
    id: Optional[int] = None
    check_item_name: Optional[str] = None     # 1. 检测项目
    check_method: Optional[str] = None        # 2. 检测方法
    unit: Optional[str] = None                # 3. 单位
    num: Optional[str] = None                 # 4. 检测结果
    detection_limit: Optional[str] = None     # 5. 检出限
    result: Optional[str] = None              # 结果判定
    reference_value: Optional[str] = None     # 参考值


class CheckObjectResponse(BaseModel):
    """检测样品列表项"""
    id: int
    check_object_union_num: str
    submission_goods_name: Optional[str] = None
    submission_person_company: Optional[str] = None
    status: int
    check_start_time: Optional[datetime] = None
    check_result: Optional[str] = None
    check_result_url: Optional[str] = None
    create_time: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CheckObjectList(BaseModel):
    """检测样品列表响应"""
    items: List[CheckObjectResponse]
    total: int
    page: int
    page_size: int


class CheckObjectDetailResponse(BaseModel):
    """检测样品详细信息"""
    id: int
    check_object_union_num: str
    submission_goods_name: Optional[str] = None
    submission_person_company: Optional[str] = None
    submission_goods_area: Optional[str] = None
    submission_goods_location: Optional[str] = None
    submission_goods_unit: Optional[str] = None
    submission_goods_car_number: Optional[str] = None
    submission_method: Optional[str] = None
    submission_person: Optional[str] = None
    submission_person_mobile: Optional[str] = None
    driver: Optional[str] = None
    driver_mobile: Optional[str] = None
    check_type: Optional[str] = None
    status: int
    check_start_time: Optional[datetime] = None
    check_end_time: Optional[datetime] = None
    check_result: Optional[str] = None
    check_result_url: Optional[str] = None
    check_items: List[CheckObjectItemResponse] = []
    create_time: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CheckObjectUpdate(BaseModel):
    """更新检测样品信息"""
    sample_name: Optional[str] = None
    company_name: Optional[str] = None
    sample_source: Optional[str] = None
    specs: Optional[str] = None
    grade: Optional[str] = None
    remark: Optional[str] = None
    status: Optional[int] = None
    check_items: Optional[List[CheckObjectItemUpdate]] = None


class CheckObjectQuery(BaseModel):
    """检测样品查询参数"""
    status: Optional[int] = None
    company: Optional[str] = None
    check_no: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=50)
