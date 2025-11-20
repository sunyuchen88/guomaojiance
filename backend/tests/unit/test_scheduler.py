"""
Unit tests for APScheduler task.
Test T078: Test job registration, execution
"""
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger


class TestScheduler:
    """T078: Unit test for APScheduler task"""

    def test_scheduler_initialization(self):
        """Test scheduler can be initialized"""
        from app.tasks.scheduler import get_scheduler

        scheduler = get_scheduler()
        assert scheduler is not None
        assert isinstance(scheduler, BackgroundScheduler)

    def test_sync_job_registration(self):
        """Test that sync job is registered correctly"""
        from app.tasks.scheduler import setup_scheduler, get_scheduler

        scheduler = get_scheduler()
        setup_scheduler(scheduler)

        jobs = scheduler.get_jobs()
        sync_job = next((j for j in jobs if 'sync' in j.id.lower()), None)

        assert sync_job is not None

    def test_sync_job_interval(self):
        """Test that sync job has correct 30-minute interval"""
        from app.tasks.scheduler import setup_scheduler, get_scheduler

        scheduler = get_scheduler()
        setup_scheduler(scheduler)

        jobs = scheduler.get_jobs()
        sync_job = next((j for j in jobs if 'sync' in j.id.lower()), None)

        if sync_job and hasattr(sync_job.trigger, 'interval'):
            # Check interval is 30 minutes (1800 seconds)
            interval_seconds = sync_job.trigger.interval.total_seconds()
            assert interval_seconds == 1800

    def test_sync_job_execution(self):
        """Test that sync job executes correctly"""
        from app.tasks.scheduler import auto_sync_task

        with patch('app.tasks.scheduler.SyncService') as mock_service:
            mock_instance = MagicMock()
            mock_service.return_value = mock_instance
            mock_instance.sync_data.return_value = {
                "status": "success",
                "fetched_count": 10
            }

            # Execute the task
            result = auto_sync_task()

            # Verify sync_data was called with auto type
            mock_instance.sync_data.assert_called_once_with(sync_type="auto")

    def test_scheduler_start(self):
        """Test scheduler starts without error"""
        from app.tasks.scheduler import get_scheduler

        scheduler = get_scheduler()

        # Start if not running
        if not scheduler.running:
            scheduler.start()
            assert scheduler.running
            scheduler.shutdown(wait=False)

    def test_scheduler_shutdown(self):
        """Test scheduler shuts down cleanly"""
        from app.tasks.scheduler import get_scheduler

        scheduler = get_scheduler()

        if not scheduler.running:
            scheduler.start()

        scheduler.shutdown(wait=False)
        assert not scheduler.running

    def test_sync_job_error_handling(self):
        """Test that sync job handles errors gracefully"""
        from app.tasks.scheduler import auto_sync_task

        with patch('app.tasks.scheduler.SyncService') as mock_service:
            mock_instance = MagicMock()
            mock_service.return_value = mock_instance
            mock_instance.sync_data.side_effect = Exception("Database error")

            # Should not raise exception
            try:
                result = auto_sync_task()
                # Error should be caught and logged
            except Exception:
                pytest.fail("auto_sync_task should catch exceptions")

    def test_storage_monitoring_job_registration(self):
        """Test that storage monitoring job is registered"""
        from app.tasks.scheduler import setup_scheduler, get_scheduler

        scheduler = get_scheduler()
        setup_scheduler(scheduler)

        jobs = scheduler.get_jobs()
        storage_job = next((j for j in jobs if 'storage' in j.id.lower()), None)

        # Storage monitoring job should exist
        assert storage_job is not None

    def test_multiple_scheduler_calls_idempotent(self):
        """Test that calling setup_scheduler multiple times is safe"""
        from app.tasks.scheduler import setup_scheduler, get_scheduler

        scheduler = get_scheduler()

        # Call setup multiple times
        setup_scheduler(scheduler)
        job_count1 = len(scheduler.get_jobs())

        setup_scheduler(scheduler)
        job_count2 = len(scheduler.get_jobs())

        # Job count should remain the same (no duplicates)
        assert job_count1 == job_count2

    def test_job_next_run_time(self):
        """Test that jobs have valid next run times"""
        from app.tasks.scheduler import setup_scheduler, get_scheduler

        scheduler = get_scheduler()
        setup_scheduler(scheduler)

        if not scheduler.running:
            scheduler.start()

        jobs = scheduler.get_jobs()
        for job in jobs:
            # Each job should have a next run time
            assert job.next_run_time is not None or job.pending

        scheduler.shutdown(wait=False)

    def test_scheduler_can_pause_and_resume(self):
        """Test scheduler pause and resume functionality"""
        from app.tasks.scheduler import get_scheduler

        scheduler = get_scheduler()

        if not scheduler.running:
            scheduler.start()

        # Pause
        scheduler.pause()

        # Resume
        scheduler.resume()

        scheduler.shutdown(wait=False)
