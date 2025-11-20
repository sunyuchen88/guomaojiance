"""
Integration test for Submit Service
Test T121: Mock client API feedback endpoint, test status 200/400
"""
import pytest
from unittest.mock import patch, MagicMock
import httpx

from app.services.submit_service import SubmitService
from app.models.check_object import CheckObject
from app.models.check_item import CheckObjectItem


class TestSubmitServiceIntegration:
    """T121: Integration test for submit service"""

    @pytest.fixture
    def submit_service(self, db_session):
        return SubmitService(db_session)

    def test_submit_to_client_api_success(self, submit_service, db_session):
        """Test successful submission to client API"""
        # Create test data
        obj = CheckObject(
            check_no="CHK-001",
            sample_name="测试样品",
            company_name="测试公司",
            status=1,
            check_result="合格",
            report_url="/reports/test.pdf"
        )
        db_session.add(obj)
        db_session.commit()

        item = CheckObjectItem(
            check_object_id=obj.id,
            check_item_name="农药残留",
            check_result="0.05mg/kg",
            result_indicator="合格"
        )
        db_session.add(item)
        db_session.commit()

        # Mock client API
        mock_response = {
            "code": 0,
            "msg": "success",
            "data": {"status": "accepted"}
        }

        with patch.object(submit_service.client_api_service, 'submit_check_result') as mock_submit:
            mock_submit.return_value = mock_response

            result = submit_service.submit_check_object(obj.id)

            assert result["success"] is True
            assert result["message"] == "提交成功"

            # Verify status updated
            db_session.refresh(obj)
            assert obj.status == 2

    def test_submit_api_returns_error_code(self, submit_service, db_session):
        """Test handling when API returns error code"""
        obj = CheckObject(
            check_no="CHK-002",
            sample_name="样品2",
            status=1,
            check_result="合格"
        )
        db_session.add(obj)
        db_session.commit()

        # Mock API error response
        mock_response = {
            "code": 1,
            "msg": "Invalid signature",
            "data": None
        }

        with patch.object(submit_service.client_api_service, 'submit_check_result') as mock_submit:
            mock_submit.return_value = mock_response

            result = submit_service.submit_check_object(obj.id)

            assert result["success"] is False
            assert "Invalid signature" in result["message"]

            # Status should not be updated
            db_session.refresh(obj)
            assert obj.status == 1

    def test_submit_with_retry_on_network_error(self, submit_service, db_session):
        """Test retry logic on network errors"""
        obj = CheckObject(
            check_no="CHK-003",
            sample_name="样品3",
            status=1,
            check_result="合格"
        )
        db_session.add(obj)
        db_session.commit()

        # Mock network error then success
        call_count = 0

        def mock_submit_with_retry(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise httpx.ConnectError("Connection failed")
            return {"code": 0, "msg": "success", "data": {}}

        with patch.object(submit_service.client_api_service, 'submit_check_result') as mock_submit:
            mock_submit.side_effect = mock_submit_with_retry

            result = submit_service.submit_check_object(obj.id)

            # Should succeed after retry
            assert result["success"] is True
            assert call_count >= 2  # At least one retry

    def test_submit_formats_data_correctly(self, submit_service, db_session):
        """Test that submit formats data according to API spec"""
        obj = CheckObject(
            check_no="CHK-004",
            sample_name="样品4",
            status=1,
            check_result="合格",
            report_url="/reports/test.pdf"
        )
        db_session.add(obj)
        db_session.commit()

        items = [
            CheckObjectItem(
                check_object_id=obj.id,
                check_item_name="项目1",
                check_result="结果1",
                result_indicator="合格"
            ),
            CheckObjectItem(
                check_object_id=obj.id,
                check_item_name="项目2",
                check_result="结果2",
                result_indicator="合格"
            )
        ]
        db_session.add_all(items)
        db_session.commit()

        captured_data = None

        def capture_submit_data(check_no, check_result, check_items, report_url=None):
            nonlocal captured_data
            captured_data = {
                "check_no": check_no,
                "check_result": check_result,
                "check_items": check_items,
                "report_url": report_url
            }
            return {"code": 0, "msg": "success", "data": {}}

        with patch.object(submit_service.client_api_service, 'submit_check_result') as mock_submit:
            mock_submit.side_effect = capture_submit_data

            submit_service.submit_check_object(obj.id)

            # Verify data format
            assert captured_data is not None
            assert captured_data["check_no"] == "CHK-004"
            assert captured_data["check_result"] == "合格"
            assert len(captured_data["check_items"]) == 2

    def test_submit_includes_report_url(self, submit_service, db_session):
        """Test that report URL is included in submission"""
        obj = CheckObject(
            check_no="CHK-005",
            sample_name="样品5",
            status=1,
            check_result="合格",
            report_url="/reports/2024/11/test.pdf"
        )
        db_session.add(obj)
        db_session.commit()

        with patch.object(submit_service.client_api_service, 'submit_check_result') as mock_submit:
            mock_submit.return_value = {"code": 0, "msg": "success", "data": {}}

            submit_service.submit_check_object(obj.id)

            # Verify report_url was passed
            call_args = mock_submit.call_args
            assert call_args[1]["report_url"] == "/reports/2024/11/test.pdf"

    def test_submit_handles_timeout(self, submit_service, db_session):
        """Test handling of request timeout"""
        obj = CheckObject(
            check_no="CHK-006",
            sample_name="样品6",
            status=1,
            check_result="合格"
        )
        db_session.add(obj)
        db_session.commit()

        with patch.object(submit_service.client_api_service, 'submit_check_result') as mock_submit:
            mock_submit.side_effect = httpx.TimeoutException("Request timed out")

            result = submit_service.submit_check_object(obj.id)

            assert result["success"] is False
            assert "timeout" in result["message"].lower() or "超时" in result["message"]
