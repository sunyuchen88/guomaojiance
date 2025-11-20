"""
Submit Service
T124, T125: Implement SubmitService
- format_check_result: Format result data for client API
- call_client_api: Submit to client feedback endpoint
- handle_response: Process response and update status
T128: Retry logic with exponential backoff
"""
import time
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
import httpx

from app.services.client_api_service import ClientAPIService
from app.models.check_object import CheckObject
from app.models.check_item import CheckObjectItem
from app.utils.security import calculate_md5_signature


class SubmitService:
    """Service for submitting check results to client API"""

    def __init__(self, db: Session):
        self.db = db
        self.client_api_service = ClientAPIService()
        self.max_retries = 3
        self.base_retry_delay = 1  # seconds

    def submit_check_object(self, check_object_id: int) -> Dict:
        """
        Submit check object results to client API

        Args:
            check_object_id: ID of check object to submit

        Returns:
            Dictionary with success status and message
        """
        # Get check object
        check_object = self.db.query(CheckObject).filter(
            CheckObject.id == check_object_id
        ).first()

        if not check_object:
            return {
                "success": False,
                "message": "检测对象不存在"
            }

        # Validate status and data
        if not self.can_submit(check_object_id):
            if check_object.status == 0:
                return {"success": False, "message": "检测对象必须是已检测状态才能提交"}
            elif check_object.status == 2:
                return {"success": False, "message": "检测对象已提交,不能重复提交"}
            else:
                return {"success": False, "message": "检测对象状态不正确"}

        if not check_object.check_result:
            return {"success": False, "message": "检验结果不能为空"}

        # Get check items
        check_items = self.db.query(CheckObjectItem).filter(
            CheckObjectItem.check_object_id == check_object_id
        ).all()

        # Format check items
        formatted_items = self.format_check_items([
            {
                "check_item_name": item.check_item_name,
                "check_result": item.check_result,
                "result_indicator": item.result_indicator
            }
            for item in check_items
        ])

        # Submit with retry logic (T128)
        for attempt in range(self.max_retries):
            try:
                # Call client API
                response = self.client_api_service.submit_check_result(
                    check_no=check_object.check_no,
                    check_result=check_object.check_result,
                    check_items=formatted_items,
                    report_url=check_object.report_url
                )

                # Handle response
                result = self.handle_client_response(response)

                if result["success"]:
                    # Update status to 2 (已提交)
                    check_object.status = 2
                    self.db.commit()

                return result

            except (httpx.ConnectError, httpx.TimeoutException) as e:
                # Network errors: retry with exponential backoff
                if attempt < self.max_retries - 1:
                    delay = self.calculate_retry_delay(attempt)
                    time.sleep(delay)
                    continue
                else:
                    return {
                        "success": False,
                        "message": f"网络错误: {str(e)},已重试{self.max_retries}次"
                    }

            except Exception as e:
                return {
                    "success": False,
                    "message": self.format_error_message(e)
                }

        return {
            "success": False,
            "message": "提交失败: 超过最大重试次数"
        }

    def can_submit(self, check_object_id: int) -> bool:
        """
        Check if check object can be submitted

        Args:
            check_object_id: ID of check object

        Returns:
            True if can submit, False otherwise
        """
        check_object = self.db.query(CheckObject).filter(
            CheckObject.id == check_object_id
        ).first()

        if not check_object:
            return False

        # Must be status 1 (已检测) and have check_result
        return check_object.status == 1 and bool(check_object.check_result)

    def format_check_items(self, check_items: List[Dict]) -> List[Dict]:
        """
        Format check items for API submission

        Args:
            check_items: List of check item dictionaries

        Returns:
            Formatted list of check items
        """
        return [
            {
                "item_name": item.get("check_item_name", ""),
                "result": item.get("check_result", ""),
                "indicator": item.get("result_indicator", "")
            }
            for item in check_items
        ]

    def validate_submit_data(self, data: Dict) -> bool:
        """
        Validate submit data

        Args:
            data: Data to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["check_no", "check_result"]
        return all(field in data and data[field] for field in required_fields)

    def generate_signature(self, data: Dict) -> str:
        """
        Generate MD5 signature for submit data (T125)

        Args:
            data: Data to sign

        Returns:
            MD5 signature in uppercase
        """
        return calculate_md5_signature(data, self.client_api_service.secret)

    def build_submit_payload(
        self,
        check_object_data: Dict,
        check_items: List[Dict]
    ) -> Dict:
        """
        Build complete submit payload with signature

        Args:
            check_object_data: Check object data
            check_items: List of check items

        Returns:
            Complete payload with signature
        """
        timestamp = str(int(time.time()))

        payload = {
            "app_id": self.client_api_service.app_id,
            "timestamp": timestamp,
            "check_no": check_object_data["check_no"],
            "check_result": check_object_data["check_result"],
            "check_items": check_items,
        }

        if check_object_data.get("report_url"):
            payload["report_url"] = check_object_data["report_url"]

        # Generate signature
        sign = self.generate_signature(payload)
        payload["sign"] = sign

        return payload

    def handle_client_response(self, response: Dict) -> Dict:
        """
        Handle client API response (T127)

        Args:
            response: API response

        Returns:
            Result dictionary with success status
        """
        if response.get("code") == 0:
            return {
                "success": True,
                "message": "提交成功"
            }
        else:
            error_msg = response.get("msg", "未知错误")
            return {
                "success": False,
                "message": f"客户端API错误: {error_msg}"
            }

    def calculate_retry_delay(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay (T128)

        Args:
            attempt: Attempt number (0-indexed)

        Returns:
            Delay in seconds
        """
        return self.base_retry_delay * (2 ** attempt)

    def format_error_message(self, error: Exception) -> str:
        """
        Format error message for user display

        Args:
            error: Exception

        Returns:
            Formatted error message
        """
        error_str = str(error)

        if "timeout" in error_str.lower():
            return "请求超时,请检查网络连接"
        elif "connection" in error_str.lower():
            return "网络连接失败,请稍后重试"
        else:
            return f"提交失败: {error_str}"
