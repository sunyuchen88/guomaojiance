"""
Client API Service
T081: Implement ClientAPIService
- fetch_check_objects: Fetch data from client API
- calculate MD5 signature: Generate authentication signature

参考已测试成功的 quality_inspection_api.py 实现
"""
import hashlib
import time
import random
import string
import json
from typing import Dict, List, Optional, Any
import httpx
from datetime import datetime, timedelta
import logging

from app.config import settings
from app.services.mock_client_api import MockClientAPIService

logger = logging.getLogger(__name__)


class ClientAPIService:
    """Service for interacting with client API"""

    def __init__(self):
        self.base_url = settings.API_BASE_URL
        self.app_id = settings.CLIENT_APP_ID
        self.key = settings.CLIENT_SECRET
        self.timeout = 30.0
        self.use_mock = settings.USE_MOCK_CLIENT_API
        self.mock_service = MockClientAPIService() if self.use_mock else None

    def _generate_random_string(self, length: int = 5) -> str:
        """生成指定长度的随机字符串"""
        return ''.join(random.choices(string.ascii_lowercase, k=length))

    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """
        生成签名

        签名规则：
        1. 将以下字段按字典序升序排列：app_id, time, random_str
        2. 拼接成字符串（使用&连接）：app_id&random_str&time
        3. 拼接key（密钥）：app_id&random_str&time&key
        4. 使用MD5对拼接后的字符串进行加密，生成32位小写签名
        """
        # 按照文档说明，只使用app_id, time, random_str三个字段参与签名计算
        sign_params = {
            'app_id': params['app_id'],
            'time': params['time'],
            'random_str': params['random_str']
        }

        # 按照字段名字典序升序排列
        sorted_keys = sorted(sign_params.keys())

        # 连接参数值
        sign_values = [str(sign_params[k]) for k in sorted_keys]
        sign_str = '&'.join(sign_values) + f"&{self.key}"

        logger.debug(f"签名字段排序: {sorted_keys}")
        logger.debug(f"签名字符串: {sign_str}")

        # 生成MD5签名（32位小写）
        signature = hashlib.md5(sign_str.encode('utf-8')).hexdigest()

        logger.debug(f"生成的签名: {signature}")

        return signature

    def _prepare_request_params(self, biz_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备请求参数

        :param biz_data: 业务数据
        :return: 完整的请求参数
        """
        params = {
            'app_id': self.app_id,
            'time': int(time.time()),
            'random_str': self._generate_random_string(),
            'biz': json.dumps(biz_data, ensure_ascii=False)
        }

        # 生成签名（注意：biz字段不参与签名计算）
        params['sign'] = self._generate_signature(params)

        logger.debug(f"完整请求参数: {params}")

        return params

    def _make_request(
        self,
        endpoint: str,
        biz_data: Dict[str, Any]
    ) -> Dict:
        """
        Make HTTP request to client API

        Args:
            endpoint: API endpoint path
            biz_data: Business data to send

        Returns:
            API response as dictionary

        Raises:
            Exception: On network/HTTP errors
        """
        url = f"{self.base_url}{endpoint}"

        # 准备请求参数
        params = self._prepare_request_params(biz_data)

        logger.info(f"Requesting: {url}")

        # Make request with form data
        with httpx.Client(timeout=self.timeout) as client:
            response = client.post(
                url,
                data=params,
                headers={'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'}
            )

            logger.info(f"API Response status: {response.status_code}")

            response.raise_for_status()

            # Parse JSON response
            try:
                json_response = response.json()
                return json_response
            except Exception as e:
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.error(f"Response content type: {response.headers.get('content-type')}")
                logger.error(f"Response text (first 500 chars): {response.text[:500]}")
                raise

    def fetch_check_objects(
        self,
        page: int = 1,
        page_size: int = 50,
        status: Optional[int] = None
    ) -> Dict:
        """
        Fetch check objects from client API

        接口1: 读取待检测样品
        端点: /admin/api/test/check/data

        Args:
            page: Page number (default: 1)
            page_size: Items per page (default: 50)
            status: Filter by status (optional)

        Returns:
            API response containing list of check objects
        """
        # Use mock data if enabled
        if self.use_mock:
            logger.info("Using MOCK client API data")
            return self.mock_service.get_mock_check_objects(page, page_size)

        endpoint = "/admin/api/test/check/data"

        # 准备业务数据 - 固定起始时间，截止时间为系统当天
        # 起始时间：2025年1月1日
        # 截止时间：系统当天
        start_time = "2025-01-01 00:00:00"
        end_time = datetime.now().strftime("%Y-%m-%d 23:59:59")

        biz_data = {
            "start_time": start_time,
            "end_time": end_time,
            "limit": page_size
        }

        logger.info(f"Fetching check objects: {start_time} to {end_time}, limit: {page_size}")

        try:
            response = self._make_request(endpoint, biz_data)

            # 转换响应格式以匹配内部期望的格式
            if response.get("status") == 200:
                # API返回格式：{"status": 200, "message": "success", "data": {"count": X, "list": [...]}}
                data = response.get("data", {})

                # 提取list和count
                if isinstance(data, dict):
                    data_list = data.get("list", [])
                    total_count = data.get("count", len(data_list))
                else:
                    # 如果data直接是列表（兼容处理）
                    data_list = data if isinstance(data, list) else []
                    total_count = len(data_list)

                logger.info(f"Successfully fetched {len(data_list)} check objects (total: {total_count})")

                return {
                    "code": 0,
                    "msg": "success",
                    "data": {
                        "list": data_list,
                        "total": total_count
                    }
                }
            else:
                error_msg = response.get("message", "未知错误")
                logger.error(f"API returned error status: {response.get('status')}, message: {error_msg}")
                return {
                    "code": response.get("status", -1),
                    "msg": error_msg,
                    "data": {"list": [], "total": 0}
                }

        except httpx.HTTPError as e:
            logger.error(f"客户端API请求失败: {str(e)}")
            raise Exception(f"客户端API请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"API响应JSON解析失败: {str(e)}")
            raise Exception(f"API响应解析失败，可能返回了非JSON内容")

    def parse_check_object(self, api_data: Dict) -> Dict:
        """
        Parse check object data from API response

        将API返回的字段映射到数据库模型字段

        Args:
            api_data: Raw check object data from API

        Returns:
            Parsed check object data matching database model
        """
        # 映射API字段到数据库字段
        parsed = {
            # 主键和标识
            "check_object_id": api_data.get("check_object_id") or api_data.get("id"),
            "check_object_union_num": api_data.get("check_no") or api_data.get("check_object_union_num"),
            "day_num": api_data.get("day_num"),

            # 送检商品信息
            "submission_goods_id": api_data.get("submission_goods_id"),
            "submission_goods_name": api_data.get("submission_goods_name") or api_data.get("sample_name"),
            "submission_goods_area": api_data.get("submission_goods_area"),
            "submission_goods_location": api_data.get("submission_goods_location"),
            "submission_goods_unit": api_data.get("submission_goods_unit"),
            "submission_goods_car_number": api_data.get("submission_goods_car_number"),

            # 送检人信息
            "submission_method": api_data.get("submission_method"),
            "submission_person": api_data.get("submission_person"),
            "submission_person_mobile": api_data.get("submission_person_mobile"),
            "submission_person_company": api_data.get("submission_person_company") or api_data.get("company_name"),

            # 司机信息
            "driver": api_data.get("driver"),
            "driver_mobile": api_data.get("driver_mobile"),

            # 检测信息
            "check_type": api_data.get("check_type"),
            "status": api_data.get("status", 0),
            "is_receive": api_data.get("is_receive", 1),
            "check_start_time": self._parse_datetime(api_data.get("check_start_time") or api_data.get("sampling_time")),
            "check_end_time": self._parse_datetime(api_data.get("check_end_time")),
            "check_result": api_data.get("check_result"),
            "check_result_url": api_data.get("check_result_url") or api_data.get("report_url"),

            # 元数据
            "create_admin": api_data.get("create_admin"),
        }

        # 解析检测项目
        # 需求2.5.2: 字段映射从 data:list:objectItems:checkItem 中取值
        check_items = []
        items_data = api_data.get("objectItems") or api_data.get("check_items") or api_data.get("item") or []

        for item_data in items_data:
            # 获取嵌套的checkItem对象（客户API返回格式）
            check_item = item_data.get("checkItem") or item_data

            check_items.append({
                "check_object_item_id": item_data.get("check_object_item_id") or item_data.get("id"),
                # 需求2.5.2: 序号 → checkItem:item_id
                "check_item_id": check_item.get("item_id") or check_item.get("check_item_id"),
                # 需求2.5.2: 检验项目 → checkItem:name
                "check_item_name": check_item.get("name") or check_item.get("check_item_name") or check_item.get("item_name"),
                # 需求2.5.2: 单位 → checkItem:reference_values
                "unit": check_item.get("reference_values"),
                # 需求2.5.2: 检出限 → checkItem:fee
                "detection_limit": check_item.get("fee"),
                # 需求2.5.2: 检测方法 → checkItem:method_name
                "check_method": check_item.get("method_name"),
                # 其他字段
                "reference_value": check_item.get("reference_value") or check_item.get("reference_values"),
                "item_indicator": check_item.get("item_indicator"),
            })

        parsed["check_items"] = check_items

        return parsed

    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object"""
        if not dt_str:
            return None

        # 如果已经是datetime对象
        if isinstance(dt_str, datetime):
            return dt_str

        try:
            # Try common formats
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y/%m/%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
                try:
                    return datetime.strptime(dt_str, fmt)
                except ValueError:
                    continue

            # 尝试ISO格式
            try:
                return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            except:
                pass

            return None
        except:
            return None

    def submit_check_result(
        self,
        check_objects: List[Dict]
    ) -> Dict:
        """
        Submit check results to client API

        接口2: 检测结果接收
        端点: /admin/api/test/check/feedback

        Args:
            check_objects: List of check objects with results

        Returns:
            API response
        """
        if self.use_mock:
            logger.info("Using MOCK client API for submit")
            return {"status": 200, "message": "提交成功(模拟)"}

        endpoint = "/admin/api/test/check/feedback"

        # 准备业务数据
        goods = []
        check_no_list = []

        for obj in check_objects:
            check_no = obj.get("check_object_union_num")
            check_no_list.append(check_no)

            # 准备检测项目结果
            items = []
            for item in obj.get("check_items", []):
                items.append({
                    "item_id": item.get("check_item_id"),
                    "item_name": item.get("check_item_name"),
                    "item_res": item.get("result", "合格"),
                    "item_indicator": item.get("num", "")
                })

            goods.append({
                "check_no": check_no,
                "check_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "check_result_url": obj.get("check_result_url", ""),
                "check_result": obj.get("check_result", "合格"),
                "item": items
            })

        biz_data = {
            "check_no_join": ",".join(check_no_list),
            "check_num": len(goods),
            "goods": goods
        }

        try:
            response = self._make_request(endpoint, biz_data)
            return response
        except httpx.HTTPError as e:
            logger.error(f"提交检测结果失败: {str(e)}")
            raise Exception(f"提交检测结果失败: {str(e)}")
