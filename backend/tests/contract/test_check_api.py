"""
Contract tests for Check Objects API endpoints.
Tests T073, T074, T075: GET /check-objects, GET /check-objects/{id}, PUT /check-objects/{id}
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, date

from app.models.check_object import CheckObject
from app.models.check_item import CheckObjectItem


class TestCheckObjectsListEndpoint:
    """T073: Contract test for GET /check-objects"""

    def test_get_check_objects_success(self, client: TestClient, auth_headers: dict, db_session):
        """Test successful retrieval of check objects list"""
        # Create test check objects
        for i in range(3):
            obj = CheckObject(
                check_no=f"CHK-2024-{i:04d}",
                sample_name=f"样品{i}",
                company_name=f"公司{i}",
                status=0,
                sampling_time=datetime.now()
            )
            db_session.add(obj)
        db_session.commit()

        response = client.get("/api/check-objects", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) == 3

    def test_check_objects_pagination(self, client: TestClient, auth_headers: dict, db_session):
        """Test pagination of check objects"""
        # Create 25 test check objects
        for i in range(25):
            obj = CheckObject(
                check_no=f"CHK-2024-{i:04d}",
                sample_name=f"样品{i}",
                company_name="测试公司",
                status=0
            )
            db_session.add(obj)
        db_session.commit()

        # Test first page with 10 items
        response = client.get("/api/check-objects?page=1&page_size=10", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 25
        assert data["page"] == 1
        assert data["page_size"] == 10

    def test_check_objects_filter_by_status(self, client: TestClient, auth_headers: dict, db_session):
        """Test filtering check objects by status"""
        # Create objects with different statuses
        for status in [0, 1, 2, 0, 1]:
            obj = CheckObject(
                check_no=f"CHK-{status}-{datetime.now().timestamp()}",
                sample_name=f"样品",
                company_name="公司",
                status=status
            )
            db_session.add(obj)
        db_session.commit()

        response = client.get("/api/check-objects?status=0", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert all(item["status"] == 0 for item in data["items"])

    def test_check_objects_filter_by_company(self, client: TestClient, auth_headers: dict, db_session):
        """Test filtering check objects by company name (fuzzy search)"""
        companies = ["北京食品公司", "上海食品厂", "广州贸易公司"]
        for i, company in enumerate(companies):
            obj = CheckObject(
                check_no=f"CHK-{i}",
                sample_name=f"样品{i}",
                company_name=company,
                status=0
            )
            db_session.add(obj)
        db_session.commit()

        response = client.get("/api/check-objects?company=食品", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2  # 北京食品公司, 上海食品厂

    def test_check_objects_filter_by_check_no(self, client: TestClient, auth_headers: dict, db_session):
        """Test filtering check objects by check_no (exact match)"""
        for i in range(3):
            obj = CheckObject(
                check_no=f"CHK-2024-{i:04d}",
                sample_name=f"样品{i}",
                company_name="公司",
                status=0
            )
            db_session.add(obj)
        db_session.commit()

        response = client.get("/api/check-objects?check_no=CHK-2024-0001", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["check_no"] == "CHK-2024-0001"

    def test_check_objects_filter_by_date_range(self, client: TestClient, auth_headers: dict, db_session):
        """Test filtering check objects by sampling date range"""
        dates = [
            datetime(2024, 1, 1),
            datetime(2024, 6, 15),
            datetime(2024, 12, 31)
        ]
        for i, dt in enumerate(dates):
            obj = CheckObject(
                check_no=f"CHK-{i}",
                sample_name=f"样品{i}",
                company_name="公司",
                status=0,
                sampling_time=dt
            )
            db_session.add(obj)
        db_session.commit()

        response = client.get(
            "/api/check-objects?start_date=2024-06-01&end_date=2024-12-31",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2  # June and December entries

    def test_check_objects_requires_authentication(self, client: TestClient):
        """Test that check objects endpoint requires authentication"""
        response = client.get("/api/check-objects")
        assert response.status_code == 401


class TestCheckObjectDetailEndpoint:
    """T074: Contract test for GET /check-objects/{id}"""

    def test_get_check_object_detail_success(self, client: TestClient, auth_headers: dict, db_session):
        """Test successful retrieval of check object detail"""
        # Create test check object with items
        obj = CheckObject(
            check_no="CHK-2024-0001",
            sample_name="测试样品",
            company_name="测试公司",
            status=0,
            sampling_time=datetime.now()
        )
        db_session.add(obj)
        db_session.commit()

        # Add check items
        for i in range(3):
            item = CheckObjectItem(
                check_object_id=obj.id,
                check_item_name=f"检测项目{i}",
                check_method=f"方法{i}",
                standard_value=f"标准{i}"
            )
            db_session.add(item)
        db_session.commit()

        response = client.get(f"/api/check-objects/{obj.id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["check_no"] == "CHK-2024-0001"
        assert data["sample_name"] == "测试样品"
        assert "check_items" in data
        assert len(data["check_items"]) == 3

    def test_get_check_object_not_found(self, client: TestClient, auth_headers: dict):
        """Test 404 when check object not found"""
        response = client.get("/api/check-objects/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_get_check_object_detail_requires_authentication(self, client: TestClient):
        """Test that check object detail endpoint requires authentication"""
        response = client.get("/api/check-objects/1")
        assert response.status_code == 401


class TestCheckObjectUpdateEndpoint:
    """T075: Contract test for PUT /check-objects/{id}"""

    def test_update_check_object_success(self, client: TestClient, auth_headers: dict, db_session):
        """Test successful update of check object"""
        # Create test check object
        obj = CheckObject(
            check_no="CHK-2024-0001",
            sample_name="原样品名",
            company_name="原公司名",
            status=0
        )
        db_session.add(obj)
        db_session.commit()

        update_data = {
            "sample_name": "新样品名",
            "company_name": "新公司名",
            "remark": "更新备注"
        }

        response = client.put(
            f"/api/check-objects/{obj.id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["sample_name"] == "新样品名"
        assert data["company_name"] == "新公司名"

    def test_update_check_object_with_items(self, client: TestClient, auth_headers: dict, db_session):
        """Test updating check object including check items"""
        # Create test check object with items
        obj = CheckObject(
            check_no="CHK-2024-0001",
            sample_name="样品",
            company_name="公司",
            status=0
        )
        db_session.add(obj)
        db_session.commit()

        item = CheckObjectItem(
            check_object_id=obj.id,
            check_item_name="检测项目1",
            check_method="方法1"
        )
        db_session.add(item)
        db_session.commit()

        update_data = {
            "sample_name": "新样品名",
            "check_items": [
                {
                    "id": item.id,
                    "check_item_name": "更新检测项目",
                    "check_method": "更新方法"
                }
            ]
        }

        response = client.put(
            f"/api/check-objects/{obj.id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["check_items"][0]["check_item_name"] == "更新检测项目"

    def test_update_check_object_not_found(self, client: TestClient, auth_headers: dict):
        """Test 404 when updating non-existent check object"""
        update_data = {"sample_name": "新名称"}
        response = client.put(
            "/api/check-objects/99999",
            json=update_data,
            headers=auth_headers
        )
        assert response.status_code == 404

    def test_update_check_object_validation_error(self, client: TestClient, auth_headers: dict, db_session):
        """Test validation error when updating with invalid data"""
        obj = CheckObject(
            check_no="CHK-2024-0001",
            sample_name="样品",
            company_name="公司",
            status=0
        )
        db_session.add(obj)
        db_session.commit()

        # Try to update with invalid status
        update_data = {"status": 99}  # Invalid status

        response = client.put(
            f"/api/check-objects/{obj.id}",
            json=update_data,
            headers=auth_headers
        )

        assert response.status_code == 422

    def test_update_check_object_requires_authentication(self, client: TestClient):
        """Test that update endpoint requires authentication"""
        response = client.put("/api/check-objects/1", json={"sample_name": "test"})
        assert response.status_code == 401
