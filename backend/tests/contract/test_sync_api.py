"""
Contract tests for Sync API endpoints.
Tests T071, T072: POST /sync/fetch, GET /sync/logs
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from datetime import datetime

from app.main import app
from app.models.sync_log import SyncLog


class TestSyncFetchEndpoint:
    """T071: Contract test for POST /sync/fetch"""

    def test_manual_sync_success(self, client: TestClient, auth_headers: dict):
        """Test successful manual sync trigger"""
        with patch('app.services.sync_service.SyncService.sync_data') as mock_sync:
            mock_sync.return_value = {
                "status": "success",
                "fetched_count": 10,
                "new_count": 5,
                "updated_count": 3,
                "message": "同步成功"
            }

            response = client.post("/api/sync/fetch", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["fetched_count"] == 10
            assert "message" in data

    def test_sync_requires_authentication(self, client: TestClient):
        """Test that sync endpoint requires authentication"""
        response = client.post("/api/sync/fetch")
        assert response.status_code == 401

    def test_sync_concurrent_control(self, client: TestClient, auth_headers: dict):
        """Test concurrent sync prevention"""
        with patch('app.services.sync_service.SyncService.sync_data') as mock_sync:
            mock_sync.side_effect = Exception("同步正在进行中，请稍后再试")

            response = client.post("/api/sync/fetch", headers=auth_headers)

            assert response.status_code == 400
            assert "同步正在进行中" in response.json()["detail"]

    def test_sync_client_api_failure(self, client: TestClient, auth_headers: dict):
        """Test handling of client API failures"""
        with patch('app.services.sync_service.SyncService.sync_data') as mock_sync:
            mock_sync.return_value = {
                "status": "error",
                "fetched_count": 0,
                "message": "客户端API连接失败"
            }

            response = client.post("/api/sync/fetch", headers=auth_headers)

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "error"


class TestSyncLogsEndpoint:
    """T072: Contract test for GET /sync/logs"""

    def test_get_sync_logs_success(self, client: TestClient, auth_headers: dict, db_session):
        """Test successful retrieval of sync logs"""
        # Create test sync logs
        for i in range(3):
            log = SyncLog(
                sync_type="manual" if i % 2 == 0 else "auto",
                status="success",
                fetched_count=10 + i,
                new_count=5 + i,
                updated_count=2 + i,
                error_message=None
            )
            db_session.add(log)
        db_session.commit()

        response = client.get("/api/sync/logs", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) == 3

    def test_sync_logs_pagination(self, client: TestClient, auth_headers: dict, db_session):
        """Test pagination of sync logs"""
        # Create 15 test sync logs
        for i in range(15):
            log = SyncLog(
                sync_type="auto",
                status="success",
                fetched_count=10,
                new_count=5,
                updated_count=2
            )
            db_session.add(log)
        db_session.commit()

        # Test first page
        response = client.get("/api/sync/logs?page=1&page_size=10", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 10
        assert data["total"] == 15
        assert data["page"] == 1

    def test_sync_logs_filter_by_type(self, client: TestClient, auth_headers: dict, db_session):
        """Test filtering sync logs by type"""
        # Create mixed sync logs
        for sync_type in ["manual", "auto", "manual"]:
            log = SyncLog(
                sync_type=sync_type,
                status="success",
                fetched_count=10,
                new_count=5,
                updated_count=2
            )
            db_session.add(log)
        db_session.commit()

        response = client.get("/api/sync/logs?sync_type=manual", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert all(item["sync_type"] == "manual" for item in data["items"])

    def test_sync_logs_filter_by_status(self, client: TestClient, auth_headers: dict, db_session):
        """Test filtering sync logs by status"""
        # Create logs with different statuses
        for status in ["success", "error", "success"]:
            log = SyncLog(
                sync_type="auto",
                status=status,
                fetched_count=10 if status == "success" else 0,
                new_count=5 if status == "success" else 0,
                updated_count=2 if status == "success" else 0,
                error_message="Error" if status == "error" else None
            )
            db_session.add(log)
        db_session.commit()

        response = client.get("/api/sync/logs?status=error", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert all(item["status"] == "error" for item in data["items"])

    def test_sync_logs_requires_authentication(self, client: TestClient):
        """Test that sync logs endpoint requires authentication"""
        response = client.get("/api/sync/logs")
        assert response.status_code == 401

    def test_sync_logs_ordered_by_created_at_desc(self, client: TestClient, auth_headers: dict, db_session):
        """Test that sync logs are ordered by created_at descending"""
        import time

        for i in range(3):
            log = SyncLog(
                sync_type="auto",
                status="success",
                fetched_count=i,
                new_count=0,
                updated_count=0
            )
            db_session.add(log)
            db_session.commit()
            time.sleep(0.01)  # Small delay to ensure different timestamps

        response = client.get("/api/sync/logs", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        items = data["items"]
        # Most recent (fetched_count=2) should be first
        assert items[0]["fetched_count"] == 2
