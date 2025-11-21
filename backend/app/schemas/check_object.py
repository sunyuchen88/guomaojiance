from pydantic import BaseModel, Field, computed_field
from datetime import datetime
from typing import Optional, List


class CheckObjectItemResponse(BaseModel):
    """检测项目信息响应 - T2.2: 5个核心字段"""
    id: int
    check_item_id: Optional[int] = None    # 需求2.5.2: 序号 (对应3.1接口的item_id)
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

    # 字段别名映射：前端使用 sample_name 和 company_name
    @computed_field
    @property
    def sample_name(self) -> Optional[str]:
        return self.submission_goods_name

    @computed_field
    @property
    def company_name(self) -> Optional[str]:
        return self.submission_person_company

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

    # 需求2.5.1新增字段 - 详情页样品基本信息
    commission_unit_address: Optional[str] = None  # 委托单位地址
    production_date: Optional[str] = "/"           # 生产日期，默认"/"
    sample_quantity: Optional[str] = None          # 样品数量
    inspection_date: Optional[str] = None          # 检测日期
    remark: Optional[str] = None                   # 备注

    check_items: List[CheckObjectItemResponse] = []
    create_time: datetime
    updated_at: Optional[datetime] = None

    # 字段别名映射：前端使用 sample_name 和 company_name
    @computed_field
    @property
    def sample_name(self) -> Optional[str]:
        return self.submission_goods_name

    @computed_field
    @property
    def company_name(self) -> Optional[str]:
        return self.submission_person_company

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

    # 需求: 所有样品基本信息字段都可编辑
    check_object_union_num: Optional[str] = None
    check_type: Optional[str] = None
    submission_person: Optional[str] = None
    submission_person_mobile: Optional[str] = None
    submission_goods_car_number: Optional[str] = None
    create_time: Optional[str] = None

    # 需求2.5.1新增字段
    commission_unit_address: Optional[str] = None  # 委托单位地址
    production_date: Optional[str] = None          # 生产日期
    sample_quantity: Optional[str] = None          # 样品数量
    inspection_date: Optional[str] = None          # 检测日期

    # 需求2.5.3: 总体检测结果和报告URL
    check_result: Optional[str] = None             # 总体检测结果（合格/不合格）
    check_result_url: Optional[str] = None         # 检测报告URL

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
