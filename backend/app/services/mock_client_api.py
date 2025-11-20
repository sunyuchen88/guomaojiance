"""
Mock Client API Service for Development/Testing
提供模拟的客户 API 响应数据，用于开发和测试
"""
from typing import Dict, List
from datetime import datetime, timedelta
import random


class MockClientAPIService:
    """提供模拟的客户 API 数据"""

    @staticmethod
    def get_mock_check_objects(page: int = 1, page_size: int = 50) -> Dict:
        """
        生成模拟的检测对象数据

        Args:
            page: 页码
            page_size: 每页数量

        Returns:
            模拟的 API 响应数据
        """
        # 生成模拟样品名称列表
        sample_names = [
            "猪肉", "牛肉", "鸡蛋", "白菜", "萝卜",
            "菠菜", "番茄", "黄瓜", "大米", "面粉",
            "食用油", "酱油", "醋", "白糖", "食盐"
        ]

        # 生成模拟公司名称
        companies = [
            "XX农产品有限公司",
            "XX食品批发市场",
            "XX超市有限公司",
            "XX农贸市场",
            "XX食品加工厂"
        ]

        # 生成模拟数据
        mock_items = []
        base_date = datetime.now() - timedelta(days=30)

        total_items = 25  # 总共生成25个样品
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_items)

        for i in range(start_idx, end_idx):
            check_object_id = 10000 + i
            sample_name = random.choice(sample_names)
            company_name = random.choice(companies)
            sampling_date = base_date + timedelta(days=random.randint(0, 30))

            mock_items.append({
                "check_object_id": check_object_id,
                "check_object_union_num": f"JC{check_object_id}",
                "day_num": sampling_date.strftime("%Y%m%d"),
                "submission_goods_name": sample_name,
                "submission_person_company": company_name,
                "submission_person": "张三",
                "submission_person_mobile": "13800138000",
                "check_type": "常规检测",
                "status": 0,  # 待检测
                "sampling_time": sampling_date.isoformat(),
                "check_items": [
                    {
                        "check_object_item_id": check_object_id * 100 + j,
                        "check_item_id": 1000 + j,
                        "check_item_name": f"检测项目{j+1}",
                        "method_name": "国标GB/T xxx",
                        "reference_value": "≤10mg/kg"
                    }
                    for j in range(3)  # 每个样品3个检测项目
                ]
            })

        return {
            "code": 0,
            "msg": "success",
            "data": {
                "list": mock_items,
                "total": total_items,
                "page": page,
                "page_size": page_size
            }
        }
