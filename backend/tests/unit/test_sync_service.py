"""
Unit tests for Sync Service.
Test T077: Test concurrency control, error handling
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import threading
import time

from app.services.sync_service import SyncService
from app.models.sync_log import SyncLog
from app.models.check_object import CheckObject


class TestSyncService:
    """T077: Unit test for sync service"""

    @pytest.fixture
    def sync_service(self, db_session):
        return SyncService(db_session)

    def test_sync_data_success(self, sync_service):
        """Test successful data synchronization"""
        mock_api_response = {
            "code": 0,
            "data": {
                "list": [
                    {
                        "check_no": "CHK-001",
                        "sample_name": "样品1",
                        "company_name": "公司1",
                        "sampling_time": "2024-01-15 10:00:00"
                    }
                ],
                "total": 1
            }
        }

        with patch.object(sync_service, 'client_api_service') as mock_client:
            mock_client.fetch_check_objects.return_value = mock_api_response

            result = sync_service.sync_data(sync_type="manual")

            assert result["status"] == "success"
            assert result["fetched_count"] == 1

    def test_sync_data_creates_new_records(self, sync_service, db_session):
        """Test that sync creates new check objects"""
        mock_api_response = {
            "code": 0,
            "data": {
                "list": [
                    {
                        "check_no": "NEW-001",
                        "sample_name": "新样品",
                        "company_name": "新公司",
                        "sampling_time": "2024-01-15 10:00:00"
                    }
                ],
                "total": 1
            }
        }

        with patch.object(sync_service, 'client_api_service') as mock_client:
            mock_client.fetch_check_objects.return_value = mock_api_response

            result = sync_service.sync_data(sync_type="manual")

            assert result["new_count"] == 1

            # Verify record was created
            obj = db_session.query(CheckObject).filter_by(check_no="NEW-001").first()
            assert obj is not None
            assert obj.sample_name == "新样品"

    def test_sync_data_updates_existing_records(self, sync_service, db_session):
        """Test that sync updates existing check objects"""
        # Create existing record
        existing = CheckObject(
            check_no="EXIST-001",
            sample_name="旧名称",
            company_name="旧公司",
            status=0
        )
        db_session.add(existing)
        db_session.commit()

        mock_api_response = {
            "code": 0,
            "data": {
                "list": [
                    {
                        "check_no": "EXIST-001",
                        "sample_name": "新名称",
                        "company_name": "新公司",
                        "sampling_time": "2024-01-15 10:00:00"
                    }
                ],
                "total": 1
            }
        }

        with patch.object(sync_service, 'client_api_service') as mock_client:
            mock_client.fetch_check_objects.return_value = mock_api_response

            result = sync_service.sync_data(sync_type="manual")

            assert result["updated_count"] == 1

    def test_sync_concurrency_control(self, sync_service):
        """Test that concurrent syncs are prevented"""
        # Simulate lock being held
        with patch.object(sync_service, 'is_sync_in_progress', return_value=True):
            with pytest.raises(Exception) as exc_info:
                sync_service.sync_data(sync_type="manual")

            assert "同步正在进行中" in str(exc_info.value)

    def test_sync_lock_acquisition_and_release(self, sync_service):
        """Test that sync lock is properly acquired and released"""
        mock_api_response = {
            "code": 0,
            "data": {"list": [], "total": 0}
        }

        with patch.object(sync_service, 'client_api_service') as mock_client:
            mock_client.fetch_check_objects.return_value = mock_api_response

            # Lock should be released after sync completes
            assert not sync_service.is_sync_in_progress()
            sync_service.sync_data(sync_type="manual")
            assert not sync_service.is_sync_in_progress()

    def test_sync_lock_released_on_error(self, sync_service):
        """Test that sync lock is released even when error occurs"""
        with patch.object(sync_service, 'client_api_service') as mock_client:
            mock_client.fetch_check_objects.side_effect = Exception("API Error")

            try:
                sync_service.sync_data(sync_type="manual")
            except:
                pass

            # Lock should still be released
            assert not sync_service.is_sync_in_progress()

    def test_sync_creates_log_on_success(self, sync_service, db_session):
        """Test that sync log is created on successful sync"""
        mock_api_response = {
            "code": 0,
            "data": {"list": [], "total": 0}
        }

        with patch.object(sync_service, 'client_api_service') as mock_client:
            mock_client.fetch_check_objects.return_value = mock_api_response

            sync_service.sync_data(sync_type="manual")

            # Verify log was created
            log = db_session.query(SyncLog).order_by(SyncLog.created_at.desc()).first()
            assert log is not None
            assert log.sync_type == "manual"
            assert log.status == "success"

    def test_sync_creates_log_on_error(self, sync_service, db_session):
        """Test that sync log is created on failed sync"""
        with patch.object(sync_service, 'client_api_service') as mock_client:
            mock_client.fetch_check_objects.side_effect = Exception("API Error")

            try:
                sync_service.sync_data(sync_type="manual")
            except:
                pass

            # Verify error log was created
            log = db_session.query(SyncLog).order_by(SyncLog.created_at.desc()).first()
            assert log is not None
            assert log.status == "error"
            assert "API Error" in log.error_message

    def test_sync_handles_empty_response(self, sync_service):
        """Test handling of empty API response"""
        mock_api_response = {
            "code": 0,
            "data": {"list": [], "total": 0}
        }

        with patch.object(sync_service, 'client_api_service') as mock_client:
            mock_client.fetch_check_objects.return_value = mock_api_response

            result = sync_service.sync_data(sync_type="manual")

            assert result["status"] == "success"
            assert result["fetched_count"] == 0

    def test_sync_handles_api_error_code(self, sync_service):
        """Test handling of API error code"""
        mock_api_response = {
            "code": 1,
            "msg": "Invalid signature",
            "data": None
        }

        with patch.object(sync_service, 'client_api_service') as mock_client:
            mock_client.fetch_check_objects.return_value = mock_api_response

            result = sync_service.sync_data(sync_type="manual")

            assert result["status"] == "error"
            assert "Invalid signature" in result["message"]

    def test_sync_type_manual(self, sync_service, db_session):
        """Test manual sync type"""
        mock_api_response = {
            "code": 0,
            "data": {"list": [], "total": 0}
        }

        with patch.object(sync_service, 'client_api_service') as mock_client:
            mock_client.fetch_check_objects.return_value = mock_api_response

            sync_service.sync_data(sync_type="manual")

            log = db_session.query(SyncLog).first()
            assert log.sync_type == "manual"

    def test_sync_type_auto(self, sync_service, db_session):
        """Test auto sync type"""
        mock_api_response = {
            "code": 0,
            "data": {"list": [], "total": 0}
        }

        with patch.object(sync_service, 'client_api_service') as mock_client:
            mock_client.fetch_check_objects.return_value = mock_api_response

            sync_service.sync_data(sync_type="auto")

            log = db_session.query(SyncLog).first()
            assert log.sync_type == "auto"

    def test_sync_does_not_update_submitted_records(self, sync_service, db_session):
        """Test that sync does not update already submitted records (status=2)"""
        # Create submitted record
        submitted = CheckObject(
            check_no="SUBMITTED-001",
            sample_name="已提交样品",
            company_name="公司",
            status=2  # Already submitted
        )
        db_session.add(submitted)
        db_session.commit()

        mock_api_response = {
            "code": 0,
            "data": {
                "list": [
                    {
                        "check_no": "SUBMITTED-001",
                        "sample_name": "新名称",  # Try to update
                        "company_name": "新公司"
                    }
                ],
                "total": 1
            }
        }

        with patch.object(sync_service, 'client_api_service') as mock_client:
            mock_client.fetch_check_objects.return_value = mock_api_response

            result = sync_service.sync_data(sync_type="manual")

            # Should not be updated
            db_session.refresh(submitted)
            assert submitted.sample_name == "已提交样品"
