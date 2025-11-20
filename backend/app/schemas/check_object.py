from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class CheckObjectItemResponse(BaseModel):
    """检测项目信息响应"""
    id: int
    check_item_name: Optional[str] = None
    check_method: Optional[str] = None
    standard_value: Optional[str] = None
    check_result: Optional[str] = None
    result_indicator: Optional[str] = None

    class Config:
        from_attributes = True


class CheckObjectItemUpdate(BaseModel):
    """更新检测项目"""
    id: Optional[int] = None
    check_item_name: Optional[str] = None
    check_method: Optional[str] = None
    standard_value: Optional[str] = None
    check_result: Optional[str] = None
    result_indicator: Optional[str] = None


class CheckObjectResponse(BaseModel):
    """检测样品列表项"""
    id: int
    check_no: str
    sample_name: Optional[str] = None
    company_name: Optional[str] = None
    status: int
    sampling_time: Optional[datetime] = None
    check_result: Optional[str] = None
    report_url: Optional[str] = None
    created_at: datetime
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
    check_no: str
    sample_name: Optional[str] = None
    company_name: Optional[str] = None
    sample_source: Optional[str] = None
    sample_base_num: Optional[str] = None
    product_date: Optional[str] = None
    specs: Optional[str] = None
    grade: Optional[str] = None
    executive_standards: Optional[str] = None
    production_license_num: Optional[str] = None
    sampling_num: Optional[str] = None
    sampling_site: Optional[str] = None
    sampling_address: Optional[str] = None
    sampling_time: Optional[datetime] = None
    commissioning_unit: Optional[str] = None
    is_subcontract: int = 0
    subcontract_lab: Optional[str] = None
    status: int
    check_result: Optional[str] = None
    report_url: Optional[str] = None
    remark: Optional[str] = None
    check_items: List[CheckObjectItemResponse] = []
    created_at: datetime
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
