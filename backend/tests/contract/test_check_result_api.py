"""
Contract tests for Check Result Input
Test T100: PUT /check-objects/{id}/result
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.check_object import CheckObject
from app.models.check_item import CheckObjectItem


class TestCheckResultEndpoint:
    """T100: Contract test for PUT /check-objects/{id}/result"""

    def test_input_check_result_success(self, client: TestClient, auth_headers: dict, db_session: Session):
        """Test successful check result input"""
        # Create test check object
        obj = CheckObject(
            check_no="CHK-2024-0001",
            sample_name="测试样品",
            company_name="测试公司",
            status=0
        )
        db_session.add(obj)
        db_session.commit()

        # Add check items
        item1 = CheckObjectItem(
            check_object_id=obj.id,
            check_item_name="农药残留",
            check_method="GB/T 20769-2008"
        )
        db_session.add(item1)
        db_session.commit()

        # Input result data
        result_data = {
            "check_result": "合格",
            "check_items": [
                {
                    "id": item1.id,
                    "check_result": "0.05mg/kg",
                    "result_indicator": "合格"
                }
            ]
        }

        response = client.put(
            f"/api/check-objects/{obj.id}/result",
            json=result_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 1  # Status should be updated to 1 (已检测)
        assert data["check_result"] == "合格"

    def test_input_result_updates_status(self, client: TestClient, auth_headers: dict, db_session: Session):
        """Test that inputting result updates status to 1"""
        obj = CheckObject(
            check_no="CHK-2024-0002",
            sample_name="样品2",
            company_name="公司2",
            status=0  # 待检测
        )
        db_session.add(obj)
        db_session.commit()

        result_data = {
            "check_result": "不合格",
            "check_items": []
        }

        response = client.put(
            f"/api/check-objects/{obj.id}/result",
            json=result_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == 1

    def test_input_result_validation_error(self, client: TestClient, auth_headers: dict, db_session: Session):
        """Test validation error when check_result is missing"""
        obj = CheckObject(
            check_no="CHK-2024-0003",
            sample_name="样品3",
            company_name="公司3",
            status=0
        )
        db_session.add(obj)
        db_session.commit()

        # Missing check_result
        result_data = {
            "check_items": []
        }

        response = client.put(
            f"/api/check-objects/{obj.id}/result",
            json=result_data,
            headers=auth_headers
        )

        assert response.status_code == 422

    def test_input_result_not_found(self, client: TestClient, auth_headers: dict):
        """Test 404 when check object not found"""
        result_data = {
            "check_result": "合格",
            "check_items": []
        }

        response = client.put(
            "/api/check-objects/99999/result",
            json=result_data,
            headers=auth_headers
        )

        assert response.status_code == 404

    def test_input_result_updates_check_items(self, client: TestClient, auth_headers: dict, db_session: Session):
        """Test that check items are updated with results"""
        obj = CheckObject(
            check_no="CHK-2024-0004",
            sample_name="样品4",
            company_name="公司4",
            status=0
        )
        db_session.add(obj)
        db_session.commit()

        item1 = CheckObjectItem(
            check_object_id=obj.id,
            check_item_name="重金属检测",
            check_method="GB 5009.12"
        )
        item2 = CheckObjectItem(
            check_object_id=obj.id,
            check_item_name="微生物检测",
            check_method="GB 4789.2"
        )
        db_session.add_all([item1, item2])
        db_session.commit()

        result_data = {
            "check_result": "合格",
            "check_items": [
                {
                    "id": item1.id,
                    "check_result": "未检出",
                    "result_indicator": "合格"
                },
                {
                    "id": item2.id,
                    "check_result": "<10 CFU/g",
                    "result_indicator": "合格"
                }
            ]
        }

        response = client.put(
            f"/api/check-objects/{obj.id}/result",
            json=result_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["check_items"]) == 2
        assert data["check_items"][0]["check_result"] == "未检出"
        assert data["check_items"][1]["result_indicator"] == "合格"

    def test_input_result_requires_authentication(self, client: TestClient, db_session: Session):
        """Test that result input requires authentication"""
        obj = CheckObject(
            check_no="CHK-2024-0005",
            sample_name="样品5",
            company_name="公司5",
            status=0
        )
        db_session.add(obj)
        db_session.commit()

        result_data = {
            "check_result": "合格",
            "check_items": []
        }

        response = client.put(
            f"/api/check-objects/{obj.id}/result",
            json=result_data
        )

        assert response.status_code == 401

    def test_cannot_modify_submitted_result(self, client: TestClient, auth_headers: dict, db_session: Session):
        """Test that cannot modify result for already submitted check object"""
        obj = CheckObject(
            check_no="CHK-2024-0006",
            sample_name="样品6",
            company_name="公司6",
            status=2  # Already submitted
        )
        db_session.add(obj)
        db_session.commit()

        result_data = {
            "check_result": "合格",
            "check_items": []
        }

        response = client.put(
            f"/api/check-objects/{obj.id}/result",
            json=result_data,
            headers=auth_headers
        )

        # Should either fail or be no-op
        assert response.status_code in [400, 403, 422]
