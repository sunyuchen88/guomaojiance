from sqlalchemy import Column, Integer, BigInteger, String, SmallInteger, Text, TIMESTAMP
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class CheckObject(Base):
    """检测样品模型 - 代表一个待检测或已检测的样品"""

    __tablename__ = "check_objects"

    # Primary keys and identifiers
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    check_object_id = Column(BigInteger, unique=True, nullable=False, index=True)
    day_num = Column(String(10), nullable=True)
    check_object_union_num = Column(String(50), nullable=False, index=True)
    code_url = Column(Text, nullable=True)

    # Submission goods information
    submission_goods_id = Column(Integer, nullable=True)
    submission_goods_name = Column(String(200), nullable=True)
    submission_goods_area = Column(String(100), nullable=True)
    submission_goods_location = Column(String(200), nullable=True)
    submission_goods_unit = Column(String(20), nullable=True)
    submission_goods_car_number = Column(String(20), nullable=True)

    # Submission information
    submission_method = Column(String(50), nullable=True)
    submission_person = Column(String(100), nullable=True)
    submission_person_mobile = Column(String(20), nullable=True)
    submission_person_company = Column(String(200), nullable=True, index=True)

    # Driver information
    driver = Column(String(100), nullable=True)
    driver_mobile = Column(String(20), nullable=True)

    # Check information
    check_type = Column(String(50), nullable=True)
    status = Column(SmallInteger, nullable=False, server_default='0', index=True)
    # status: 0=待检测, 1=已检测, 2=提交成功, 3=提交失败 (需求2.3: 4种状态)
    is_receive = Column(SmallInteger, nullable=True, server_default='1')
    check_start_time = Column(TIMESTAMP, nullable=True, index=True)
    check_end_time = Column(TIMESTAMP, nullable=True)
    check_result = Column(String(20), nullable=True)
    check_result_url = Column(Text, nullable=True)

    # 需求2.5.1新增字段 - 详情页样品基本信息
    commission_unit_address = Column(String(500), nullable=True)  # 委托单位地址
    production_date = Column(String(50), nullable=True, server_default='/')  # 生产日期，默认"/"
    sample_quantity = Column(String(50), nullable=True)  # 样品数量
    inspection_date = Column(String(50), nullable=True)  # 检测日期
    remark = Column(Text, nullable=True)  # 备注

    # Metadata
    create_admin = Column(String(100), nullable=True)
    create_time = Column(TIMESTAMP, server_default=func.now())
    synced_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    check_items = relationship(
        "CheckObjectItem",
        back_populates="check_object",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self):
        return (
            f"<CheckObject(id={self.id}, "
            f"union_num='{self.check_object_union_num}', "
            f"status={self.status})>"
        )
