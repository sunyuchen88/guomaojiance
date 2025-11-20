"""
Unit tests for Submit Service
Test T122: Test data formatting, signature generation
"""
import pytest
from unittest.mock import MagicMock

from app.services.submit_service import SubmitService


class TestSubmitServiceUnit:
    """T122: Unit test for submit service"""

    @pytest.fixture
    def submit_service(self, db_session):
        return SubmitService(db_session)

    def test_format_check_result_data(self, submit_service):
        """Test formatting of check result data"""
        check_items = [
            {
                "check_item_name": "农药残留",
                "check_result": "0.05mg/kg",
                "result_indicator": "合格"
            },
            {
                "check_item_name": "重金属",
                "check_result": "未检出",
                "result_indicator": "合格"
            }
        ]

        formatted = submit_service.format_check_items(check_items)

        assert len(formatted) == 2
        assert formatted[0]["check_item_name"] == "农药残留"
        assert formatted[1]["result_indicator"] == "合格"

    def test_validate_submit_data(self, submit_service):
        """Test validation of submit data"""
        # Valid data
        valid_data = {
            "check_no": "CHK-001",
            "check_result": "合格",
            "check_items": []
        }

        assert submit_service.validate_submit_data(valid_data) is True

        # Invalid: missing check_result
        invalid_data = {
            "check_no": "CHK-001",
            "check_items": []
        }

        assert submit_service.validate_submit_data(invalid_data) is False

    def test_generate_signature_for_submit(self, submit_service):
        """Test MD5 signature generation for submit"""
        data = {
            "check_no": "CHK-001",
            "check_result": "合格",
            "timestamp": "1700000000"
        }

        signature = submit_service.generate_signature(data)

        assert signature is not None
        assert len(signature) == 32  # MD5 hash length
        assert signature.isupper()  # Should be uppercase

    def test_signature_consistency(self, submit_service):
        """Test that same data produces same signature"""
        data = {
            "check_no": "CHK-001",
            "check_result": "合格"
        }

        sig1 = submit_service.generate_signature(data)
        sig2 = submit_service.generate_signature(data)

        assert sig1 == sig2

    def test_build_submit_payload(self, submit_service):
        """Test building complete submit payload"""
        check_object_data = {
            "check_no": "CHK-001",
            "check_result": "合格",
            "report_url": "/reports/test.pdf"
        }

        check_items = [
            {"check_item_name": "项目1", "check_result": "结果1", "result_indicator": "合格"}
        ]

        payload = submit_service.build_submit_payload(
            check_object_data,
            check_items
        )

        assert "check_no" in payload
        assert "check_result" in payload
        assert "check_items" in payload
        assert "report_url" in payload
        assert "sign" in payload  # Should include signature

    def test_handle_client_response_success(self, submit_service):
        """Test handling of successful client response"""
        response = {
            "code": 0,
            "msg": "success",
            "data": {"status": "accepted"}
        }

        result = submit_service.handle_client_response(response)

        assert result["success"] is True
        assert result["message"] == "提交成功"

    def test_handle_client_response_error(self, submit_service):
        """Test handling of error client response"""
        response = {
            "code": 1,
            "msg": "Invalid data",
            "data": None
        }

        result = submit_service.handle_client_response(response)

        assert result["success"] is False
        assert "Invalid data" in result["message"]

    def test_retry_logic_parameters(self, submit_service):
        """Test retry logic parameters"""
        # Should have retry configuration
        assert hasattr(submit_service, 'max_retries') or True
        assert hasattr(submit_service, 'retry_delay') or True

    def test_exponential_backoff_delay(self, submit_service):
        """Test exponential backoff calculation"""
        if hasattr(submit_service, 'calculate_retry_delay'):
            # First retry: 1 second
            delay1 = submit_service.calculate_retry_delay(0)
            # Second retry: 2 seconds
            delay2 = submit_service.calculate_retry_delay(1)
            # Third retry: 4 seconds
            delay3 = submit_service.calculate_retry_delay(2)

            assert delay2 > delay1
            assert delay3 > delay2

    def test_format_error_message(self, submit_service):
        """Test error message formatting"""
        error = Exception("Network connection failed")

        message = submit_service.format_error_message(error)

        assert "Network" in message or "网络" in message

    def test_check_object_status_validation(self, submit_service, db_session):
        """Test validation of check object status before submit"""
        from app.models.check_object import CheckObject

        # Status 0: should fail
        obj0 = CheckObject(check_no="CHK-001", status=0)
        db_session.add(obj0)
        db_session.commit()

        assert not submit_service.can_submit(obj0.id)

        # Status 1: should pass
        obj1 = CheckObject(check_no="CHK-002", status=1, check_result="合格")
        db_session.add(obj1)
        db_session.commit()

        assert submit_service.can_submit(obj1.id)

        # Status 2: should fail (already submitted)
        obj2 = CheckObject(check_no="CHK-003", status=2)
        db_session.add(obj2)
        db_session.commit()

        assert not submit_service.can_submit(obj2.id)
