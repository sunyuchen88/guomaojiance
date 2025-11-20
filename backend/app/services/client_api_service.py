"""
Client API Service
T081: Implement ClientAPIService
- fetch_check_objects: Fetch data from client API
- calculate MD5 signature: Generate authentication signature
"""
import hashlib
import time
from typing import Dict, List, Optional, Any
import httpx
from datetime import datetime

from app.config import settings
from app.utils.security import calculate_md5_signature


class ClientAPIService:
    """Service for interacting with client API"""

    def __init__(self):
        self.base_url = settings.API_BASE_URL
        self.app_id = settings.CLIENT_APP_ID
        self.secret = settings.CLIENT_SECRET
        self.timeout = 30.0

    def generate_signature(self, params: Dict[str, Any]) -> str:
        """
        Generate MD5 signature for API authentication

        Args:
            params: Request parameters

        Returns:
            MD5 signature in uppercase
        """
        return calculate_md5_signature(params, self.secret)

    def _make_request(
        self,
        endpoint: str,
        method: str = "POST",
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Dict:
        """
        Make HTTP request to client API

        Args:
            endpoint: API endpoint path
            method: HTTP method
            params: Query parameters
            data: Request body data

        Returns:
            API response as dictionary

        Raises:
            httpx.HTTPError: On network/HTTP errors
        """
        url = f"{self.base_url}{endpoint}"

        # Add timestamp
        timestamp = str(int(time.time()))

        # Prepare request parameters
        request_params = {
            "app_id": self.app_id,
            "timestamp": timestamp,
        }

        if params:
            request_params.update(params)

        # Generate signature
        sign = self.generate_signature(request_params)
        request_params["sign"] = sign

        # Make request
        with httpx.Client(timeout=self.timeout) as client:
            if method.upper() == "POST":
                response = client.post(url, json=request_params)
            else:
                response = client.get(url, params=request_params)

            response.raise_for_status()
            return response.json()

    def fetch_check_objects(
        self,
        page: int = 1,
        page_size: int = 50,
        status: Optional[int] = None
    ) -> Dict:
        """
        Fetch check objects from client API

        Args:
            page: Page number (default: 1)
            page_size: Items per page (default: 50)
            status: Filter by status (optional)

        Returns:
            API response containing list of check objects

        Example response:
            {
                "code": 0,
                "msg": "success",
                "data": {
                    "list": [...],
                    "total": 100
                }
            }
        """
        endpoint = "/api/check/objects"

        params = {
            "page": page,
            "page_size": page_size
        }

        if status is not None:
            params["status"] = status

        try:
            response = self._make_request(endpoint, method="POST", params=params)
            return response
        except httpx.HTTPError as e:
            raise Exception(f"客户端API请求失败: {str(e)}")

    def parse_check_object(self, api_data: Dict) -> Dict:
        """
        Parse check object data from API response

        Args:
            api_data: Raw check object data from API

        Returns:
            Parsed check object data
        """
        parsed = {
            "check_no": api_data.get("check_no"),
            "sample_name": api_data.get("sample_name"),
            "company_name": api_data.get("company_name"),
            "sample_source": api_data.get("sample_source"),
            "sample_base_num": api_data.get("sample_base_num"),
            "product_date": api_data.get("product_date"),
            "specs": api_data.get("specs"),
            "grade": api_data.get("grade"),
            "executive_standards": api_data.get("executive_standards"),
            "production_license_num": api_data.get("production_license_num"),
            "sampling_num": api_data.get("sampling_num"),
            "sampling_site": api_data.get("sampling_site"),
            "sampling_address": api_data.get("sampling_address"),
            "sampling_time": self._parse_datetime(api_data.get("sampling_time")),
            "commissioning_unit": api_data.get("commissioning_unit"),
            "is_subcontract": api_data.get("is_subcontract", 0),
            "subcontract_lab": api_data.get("subcontract_lab"),
            "status": api_data.get("status", 0),
            "check_result": api_data.get("check_result"),
            "report_url": api_data.get("report_url"),
            "remark": api_data.get("remark")
        }

        # Parse check items
        check_items = []
        for item_data in api_data.get("check_items", []):
            check_items.append({
                "check_item_name": item_data.get("item_name"),
                "check_method": item_data.get("method"),
                "standard_value": item_data.get("standard_value"),
                "check_result": item_data.get("result"),
                "result_indicator": item_data.get("indicator")
            })

        parsed["check_items"] = check_items

        return parsed

    def _parse_datetime(self, dt_str: Optional[str]) -> Optional[datetime]:
        """Parse datetime string to datetime object"""
        if not dt_str:
            return None

        try:
            # Try common formats
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y/%m/%d %H:%M:%S"]:
                try:
                    return datetime.strptime(dt_str, fmt)
                except ValueError:
                    continue
            return None
        except:
            return None

    def submit_check_result(
        self,
        check_no: str,
        check_result: str,
        check_items: List[Dict],
        report_url: Optional[str] = None
    ) -> Dict:
        """
        Submit check result to client API

        Args:
            check_no: Check object number
            check_result: Overall check result
            check_items: List of check item results
            report_url: URL of report PDF

        Returns:
            API response
        """
        endpoint = "/api/check/feedback"

        data = {
            "check_no": check_no,
            "check_result": check_result,
            "check_items": check_items,
            "report_url": report_url,
            "submit_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            response = self._make_request(endpoint, method="POST", params=data)
            return response
        except httpx.HTTPError as e:
            raise Exception(f"提交检测结果失败: {str(e)}")
