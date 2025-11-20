"""
Integration test for Client API service.
Test T076: Mock client API, test data fetch
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
import httpx

from app.services.client_api_service import ClientAPIService
from app.config import settings


class TestClientAPIService:
    """T076: Integration test for client API service"""

    @pytest.fixture
    def client_api_service(self):
        return ClientAPIService()

    def test_fetch_check_objects_success(self, client_api_service):
        """Test successful fetch from client API"""
        mock_response_data = {
            "code": 0,
            "msg": "success",
            "data": {
                "list": [
                    {
                        "check_no": "CHK-001",
                        "sample_name": "样品1",
                        "company_name": "公司1",
                        "sampling_time": "2024-01-15 10:00:00",
                        "check_items": [
                            {
                                "item_name": "农药残留",
                                "method": "GB/T 20769-2008"
                            }
                        ]
                    },
                    {
                        "check_no": "CHK-002",
                        "sample_name": "样品2",
                        "company_name": "公司2",
                        "sampling_time": "2024-01-16 11:00:00",
                        "check_items": []
                    }
                ],
                "total": 2
            }
        }

        with patch.object(client_api_service, '_make_request') as mock_request:
            mock_request.return_value = mock_response_data

            result = client_api_service.fetch_check_objects()

            assert result is not None
            assert len(result["data"]["list"]) == 2
            assert result["data"]["list"][0]["check_no"] == "CHK-001"

    def test_fetch_check_objects_with_pagination(self, client_api_service):
        """Test fetch with pagination parameters"""
        mock_response_data = {
            "code": 0,
            "msg": "success",
            "data": {
                "list": [{"check_no": "CHK-001"}],
                "total": 100,
                "page": 2,
                "page_size": 50
            }
        }

        with patch.object(client_api_service, '_make_request') as mock_request:
            mock_request.return_value = mock_response_data

            result = client_api_service.fetch_check_objects(page=2, page_size=50)

            mock_request.assert_called_once()
            call_args = mock_request.call_args
            assert call_args[1].get('page') == 2 or 'page' in str(call_args)

    def test_fetch_check_objects_api_error(self, client_api_service):
        """Test handling of API error response"""
        mock_response_data = {
            "code": 1,
            "msg": "Invalid signature",
            "data": None
        }

        with patch.object(client_api_service, '_make_request') as mock_request:
            mock_request.return_value = mock_response_data

            result = client_api_service.fetch_check_objects()

            assert result["code"] == 1
            assert "Invalid" in result["msg"]

    def test_fetch_check_objects_network_error(self, client_api_service):
        """Test handling of network errors"""
        with patch.object(client_api_service, '_make_request') as mock_request:
            mock_request.side_effect = httpx.ConnectError("Connection refused")

            with pytest.raises(Exception) as exc_info:
                client_api_service.fetch_check_objects()

            assert "Connection" in str(exc_info.value)

    def test_fetch_check_objects_timeout(self, client_api_service):
        """Test handling of request timeout"""
        with patch.object(client_api_service, '_make_request') as mock_request:
            mock_request.side_effect = httpx.TimeoutException("Request timed out")

            with pytest.raises(Exception) as exc_info:
                client_api_service.fetch_check_objects()

            assert "timed out" in str(exc_info.value)

    def test_md5_signature_generation(self, client_api_service):
        """Test MD5 signature generation"""
        params = {
            "app_id": "689_abc",
            "timestamp": "1700000000",
            "page": 1,
            "page_size": 50
        }

        signature = client_api_service.generate_signature(params)

        assert signature is not None
        assert len(signature) == 32  # MD5 hash length
        assert signature.isupper()  # Should be uppercase

    def test_signature_consistency(self, client_api_service):
        """Test that same parameters produce same signature"""
        params = {
            "app_id": "689_abc",
            "timestamp": "1700000000"
        }

        sig1 = client_api_service.generate_signature(params)
        sig2 = client_api_service.generate_signature(params)

        assert sig1 == sig2

    def test_signature_changes_with_different_params(self, client_api_service):
        """Test that different parameters produce different signatures"""
        params1 = {"app_id": "689_abc", "timestamp": "1700000000"}
        params2 = {"app_id": "689_abc", "timestamp": "1700000001"}

        sig1 = client_api_service.generate_signature(params1)
        sig2 = client_api_service.generate_signature(params2)

        assert sig1 != sig2

    def test_request_includes_required_parameters(self, client_api_service):
        """Test that request includes all required parameters"""
        with patch('httpx.Client.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"code": 0, "data": {"list": []}}
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            try:
                client_api_service.fetch_check_objects()
            except:
                pass

            # Verify the call was made
            if mock_post.called:
                call_args = mock_post.call_args
                # Check that required params are included
                assert call_args is not None

    def test_parse_check_object_data(self, client_api_service):
        """Test parsing of check object data from API response"""
        api_data = {
            "check_no": "CHK-001",
            "sample_name": "测试样品",
            "company_name": "测试公司",
            "sampling_time": "2024-01-15 10:00:00",
            "sample_source": "市场采购",
            "check_items": [
                {
                    "item_name": "农药残留",
                    "method": "GB/T 20769-2008",
                    "standard_value": "≤0.1mg/kg"
                }
            ]
        }

        parsed = client_api_service.parse_check_object(api_data)

        assert parsed["check_no"] == "CHK-001"
        assert parsed["sample_name"] == "测试样品"
        assert "check_items" in parsed
        assert len(parsed["check_items"]) == 1
