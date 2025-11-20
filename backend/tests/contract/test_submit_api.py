"""
Contract tests for Submit API
Test T120: POST /submit/{check_object_id}
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock

from app.models.check_object import CheckObject
from app.models.check_item import CheckObjectItem


class TestSubmitEndpoint:
    """T120: Contract test for POST /submit/{check_object_id}"""

    def test_submit_success(self, client: TestClient, auth_headers: dict, db_session: Session):
        """Test successful submission to client API"""
        # Create test check object with status=1 (已检测)
        obj = CheckObject(
            check_no="CHK-2024-0001",
            sample_name="测试样品",
            company_name="测试公司",
            status=1,
            check_result="合格",
            report_url="/reports/2024/11/test.pdf"
        )
        db_session.add(obj)
        db_session.commit()

        # Add check items with results
        item = CheckObjectItem(
            check_object_id=obj.id,
            check_item_name="农药残留",
            check_method="GB/T 20769-2008",
            check_result="0.05mg/kg",
            result_indicator="合格"
        )
        db_session.add(item)
        db_session.commit()

        # Mock client API response
        with patch('app.services.submit_service.SubmitService.call_client_api') as mock_call:
            mock_call.return_value = {
                "code": 0,
                "msg": "success",
                "data": {"status": "accepted"}
            }

            response = client.post(
                f"/api/submit/{obj.id}",
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "提交成功"

            # Verify status updated to 2 (已提交)
            db_session.refresh(obj)
            assert obj.status == 2

    def test_submit_requires_status_1(self, client: TestClient, auth_headers: dict, db_session: Session):
        """Test that only status=1 (已检测) can be submitted"""
        # Create check object with status=0 (待检测)
        obj = CheckObject(
            check_no="CHK-2024-0002",
            sample_name="样品2",
            company_name="公司2",
            status=0
        )
        db_session.add(obj)
        db_session.commit()

        response = client.post(
            f"/api/submit/{obj.id}",
            headers=auth_headers
        )

        assert response.status_code == 400
        assert "必须是已检测状态" in response.json()["detail"]

    def test_submit_already_submitted(self, client: TestClient, auth_headers: dict, db_session: Session):
        """Test that already submitted objects cannot be re-submitted"""
        obj = CheckObject(
            check_no="CHK-2024-0003",
            sample_name="样品3",
            company_name="公司3",
            status=2  # Already submitted
        )
        db_session.add(obj)
        db_session.commit()

        response = client.post(
            f"/api/submit/{obj.id}",
            headers=auth_headers
        )

        assert response.status_code == 400
        assert "已提交" in response.json()["detail"]

    def test_submit_not_found(self, client: TestClient, auth_headers: dict):
        """Test 404 when check object not found"""
        response = client.post(
            "/api/submit/99999",
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_submit_client_api_error(self, client: TestClient, auth_headers: dict, db_session: Session):
        """Test handling of client API error response"""
        obj = CheckObject(
            check_no="CHK-2024-0004",
            sample_name="样品4",
            company_name="公司4",
            status=1,
            check_result="合格"
        )
        db_session.add(obj)
        db_session.commit()

        # Mock client API error
        with patch('app.services.submit_service.SubmitService.call_client_api') as mock_call:
            mock_call.return_value = {
                "code": 1,
                "msg": "Invalid data format",
                "data": None
            }

            response = client.post(
                f"/api/submit/{obj.id}",
                headers=auth_headers
            )

            assert response.status_code == 400
            assert "Invalid data format" in response.json()["detail"]

            # Status should remain 1 (not updated)
            db_session.refresh(obj)
            assert obj.status == 1

    def test_submit_network_error(self, client: TestClient, auth_headers: dict, db_session: Session):
        """Test handling of network errors"""
        obj = CheckObject(
            check_no="CHK-2024-0005",
            sample_name="样品5",
            company_name="公司5",
            status=1,
            check_result="合格"
        )
        db_session.add(obj)
        db_session.commit()

        # Mock network error
        with patch('app.services.submit_service.SubmitService.call_client_api') as mock_call:
            mock_call.side_effect = Exception("Network connection failed")

            response = client.post(
                f"/api/submit/{obj.id}",
                headers=auth_headers
            )

            assert response.status_code == 500
            assert "Network" in response.json()["detail"] or "失败" in response.json()["detail"]

    def test_submit_requires_authentication(self, client: TestClient, db_session: Session):
        """Test that submit requires authentication"""
        obj = CheckObject(
            check_no="CHK-2024-0006",
            sample_name="样品6",
            company_name="公司6",
            status=1
        )
        db_session.add(obj)
        db_session.commit()

        response = client.post(f"/api/submit/{obj.id}")
        assert response.status_code == 401

    def test_submit_requires_check_result(self, client: TestClient, auth_headers: dict, db_session: Session):
        """Test that check_result must be present"""
        obj = CheckObject(
            check_no="CHK-2024-0007",
            sample_name="样品7",
            company_name="公司7",
            status=1,
            check_result=None  # No result
        )
        db_session.add(obj)
        db_session.commit()

        response = client.post(
            f"/api/submit/{obj.id}",
            headers=auth_headers
        )

        assert response.status_code == 400
        assert "检验结果" in response.json()["detail"]
