"""
APScheduler Setup
T084: Implement APScheduler setup
- Daily job at 2:00 AM calling SyncService (每天自动同步一次)
- Storage monitoring job at 3:00 AM
- Manual sync available via API endpoint
"""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from app.database import SessionLocal
from app.services.sync_service import SyncService
from app.utils.storage import check_storage_space

logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler: BackgroundScheduler = None


def get_scheduler() -> BackgroundScheduler:
    """Get or create scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = BackgroundScheduler()
    return _scheduler


def auto_sync_task():
    """
    Task for automatic data synchronization
    Runs daily at 2:00 AM (每天凌晨2点自动同步一次)
    """
    logger.info("Starting automatic sync task")

    db = SessionLocal()
    try:
        sync_service = SyncService(db)
        result = sync_service.sync_data(sync_type="auto")

        if result["status"] == "success":
            logger.info(
                f"Auto sync completed: fetched={result['fetched_count']}, "
                f"new={result['new_count']}, updated={result['updated_count']}"
            )
        else:
            logger.warning(f"Auto sync failed: {result['message']}")

        return result

    except Exception as e:
        logger.error(f"Auto sync task error: {str(e)}")
        return {"status": "error", "message": str(e)}

    finally:
        db.close()


def storage_monitor_task():
    """
    Task for monitoring disk storage
    Runs daily to check available disk space
    """
    logger.info("Running storage monitoring task")

    try:
        result = check_storage_space("/app/uploads", threshold_gb=10)

        if result["is_low"]:
            logger.warning(
                f"Low disk space warning: {result['free_gb']:.2f}GB free, "
                f"threshold is {result['threshold_gb']}GB at {result['path']}"
            )
        else:
            logger.info(
                f"Disk space OK: {result['free_gb']:.2f}GB free "
                f"({result['usage_percent']:.1f}% used) at {result['path']}"
            )

        return result

    except Exception as e:
        logger.error(f"Storage monitor task error: {str(e)}")
        return {"status": "error", "message": str(e)}


def setup_scheduler(scheduler: BackgroundScheduler):
    """
    Setup scheduler with all jobs

    Args:
        scheduler: BackgroundScheduler instance
    """
    # Remove existing jobs to avoid duplicates
    existing_jobs = {job.id for job in scheduler.get_jobs()}

    # Add sync job - daily at 2:00 AM (每天自动同步一次)
    if "auto_sync_job" not in existing_jobs:
        scheduler.add_job(
            auto_sync_task,
            trigger=CronTrigger(hour=2, minute=0),
            id="auto_sync_job",
            name="Automatic Data Sync",
            replace_existing=True,
            max_instances=1  # Prevent concurrent runs
        )
        logger.info("Added auto sync job (daily at 2:00 AM)")

    # Add storage monitoring job - daily at 3:00 AM
    if "storage_monitor_job" not in existing_jobs:
        scheduler.add_job(
            storage_monitor_task,
            trigger=CronTrigger(hour=3, minute=0),
            id="storage_monitor_job",
            name="Storage Monitoring",
            replace_existing=True
        )
        logger.info("Added storage monitor job (daily at 3:00 AM)")


def start_scheduler():
    """Start the scheduler"""
    scheduler = get_scheduler()
    setup_scheduler(scheduler)

    if not scheduler.running:
        scheduler.start()
        logger.info("Scheduler started")


def shutdown_scheduler():
    """Shutdown the scheduler"""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Scheduler shutdown")
