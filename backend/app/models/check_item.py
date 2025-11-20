from sqlalchemy import (
    Column, Integer, BigInteger, String, SmallInteger,
    TIMESTAMP, ForeignKey, Numeric
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class CheckObjectItem(Base):
    """检测项目明细模型 - 代表样品中的具体检测项目"""

    __tablename__ = "check_object_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    check_object_item_id = Column(BigInteger, unique=True, nullable=False)
    check_object_id = Column(
        BigInteger,
        ForeignKey("check_objects.check_object_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    check_item_id = Column(Integer, nullable=False)
    check_item_name = Column(String(200), nullable=False)

    # T2.2: 5个核心字段 - 检测项目、单位、检测结果、检出限、检测方法
    check_method = Column(String(200), nullable=True)  # 检测方法
    unit = Column(String(50), nullable=True)  # 单位
    detection_limit = Column(String(100), nullable=True)  # 检出限

    # Check results
    num = Column(String(50), nullable=True)  # 检测结果数值
    result = Column(String(20), nullable=True)  # 合格/不合格
    check_time = Column(TIMESTAMP, nullable=True)
    check_admin = Column(String(100), nullable=True)
    status = Column(SmallInteger, nullable=True, server_default='1')

    # Reference data
    create_time = Column(TIMESTAMP, server_default=func.now())
    reference_value = Column(String(100), nullable=True)
    item_indicator = Column(String(200), nullable=True)

    # Relationships
    check_object = relationship("CheckObject", back_populates="check_items")

    def __repr__(self):
        return (
            f"<CheckObjectItem(id={self.id}, "
            f"check_item_name='{self.check_item_name}', "
            f"result='{self.result}')>"
        )


class CheckItem(Base):
    """检测项目基础表 - 存储检测项目的基础信息"""

    __tablename__ = "check_items"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    item_id = Column(Integer, unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False, index=True)

    # Method information
    method_id = Column(Integer, nullable=True)
    method_name = Column(String(200), nullable=True)

    # Standard information
    basic_id = Column(Integer, nullable=True)
    basic_name = Column(String(500), nullable=True)

    # Indicators
    indicators_id = Column(Integer, nullable=True)
    indicators_name = Column(String(200), nullable=True)
    reference_values = Column(String(100), nullable=True)

    # Metadata
    fee = Column(Numeric(10, 2), nullable=True, server_default='0.01')
    created_at = Column(TIMESTAMP, server_default=func.now())

    def __repr__(self):
        return f"<CheckItem(id={self.id}, name='{self.name}', method='{self.method_name}')>"
