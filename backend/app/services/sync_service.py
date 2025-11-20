"""
Sync Service
T082, T083: Implement SyncService
- sync_data: Synchronize data from client API
- Handle concurrency control
- Log sync results
"""
import threading
from typing import Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.services.client_api_service import ClientAPIService
from app.models.check_object import CheckObject
from app.models.check_item import CheckObjectItem
from app.models.sync_log import SyncLog


class SyncService:
    """Service for synchronizing data from client API"""

    # Class-level lock for concurrency control
    _sync_lock = threading.Lock()
    _is_syncing = False

    def __init__(self, db: Session):
        self.db = db
        self.client_api_service = ClientAPIService()

    @classmethod
    def is_sync_in_progress(cls) -> bool:
        """Check if sync is currently in progress"""
        return cls._is_syncing

    def sync_data(self, sync_type: str = "manual") -> Dict:
        """
        Synchronize check objects from client API

        Args:
            sync_type: Type of sync - "manual" or "auto"

        Returns:
            Dictionary with sync results:
            {
                "status": "success" | "error",
                "fetched_count": int,
                "new_count": int,
                "updated_count": int,
                "message": str
            }

        Raises:
            Exception: If sync is already in progress or API error occurs
        """
        # Check if sync is already running
        if not self._sync_lock.acquire(blocking=False):
            raise Exception("同步正在进行中,请稍后再试")

        try:
            self.__class__._is_syncing = True

            # Initialize counters
            fetched_count = 0
            new_count = 0
            updated_count = 0
            error_message = None

            try:
                # Fetch data from client API
                response = self.client_api_service.fetch_check_objects(
                    page=1,
                    page_size=100  # Fetch first 100 records
                )

                # Check API response code
                if response.get("code") != 0:
                    error_message = response.get("msg", "未知错误")
                    self._create_sync_log(
                        sync_type=sync_type,
                        status="error",
                        fetched_count=0,
                        new_count=0,
                        updated_count=0,
                        error_message=error_message
                    )
                    return {
                        "status": "error",
                        "fetched_count": 0,
                        "new_count": 0,
                        "updated_count": 0,
                        "message": error_message
                    }

                # Parse data
                data_list = response.get("data", {}).get("list", [])
                fetched_count = len(data_list)

                # Process each check object
                for api_data in data_list:
                    parsed_data = self.client_api_service.parse_check_object(api_data)

                    # Check if record exists
                    existing = self.db.query(CheckObject).filter(
                        CheckObject.check_no == parsed_data["check_no"]
                    ).first()

                    if existing:
                        # Don't update if already submitted (status=2)
                        if existing.status != 2:
                            # Update existing record
                            for key, value in parsed_data.items():
                                if key != "check_items" and value is not None:
                                    setattr(existing, key, value)

                            # Update check items
                            self._update_check_items(existing, parsed_data["check_items"])
                            updated_count += 1
                    else:
                        # Create new record
                        check_items = parsed_data.pop("check_items", [])
                        new_obj = CheckObject(**parsed_data)
                        self.db.add(new_obj)
                        self.db.flush()  # Get ID for items

                        # Add check items
                        for item_data in check_items:
                            item = CheckObjectItem(
                                check_object_id=new_obj.id,
                                **item_data
                            )
                            self.db.add(item)

                        new_count += 1

                # Commit all changes
                self.db.commit()

                # Create success log
                self._create_sync_log(
                    sync_type=sync_type,
                    status="success",
                    fetched_count=fetched_count,
                    new_count=new_count,
                    updated_count=updated_count,
                    error_message=None
                )

                return {
                    "status": "success",
                    "fetched_count": fetched_count,
                    "new_count": new_count,
                    "updated_count": updated_count,
                    "message": f"同步成功: 获取{fetched_count}条, 新增{new_count}条, 更新{updated_count}条"
                }

            except Exception as e:
                self.db.rollback()
                error_message = str(e)

                # Create error log
                self._create_sync_log(
                    sync_type=sync_type,
                    status="error",
                    fetched_count=fetched_count,
                    new_count=new_count,
                    updated_count=updated_count,
                    error_message=error_message
                )

                return {
                    "status": "error",
                    "fetched_count": 0,
                    "new_count": 0,
                    "updated_count": 0,
                    "message": f"同步失败: {error_message}"
                }

        finally:
            # Always release lock
            self.__class__._is_syncing = False
            self._sync_lock.release()

    def _update_check_items(self, check_object: CheckObject, items_data: list):
        """Update check items for a check object"""
        # Remove existing items
        self.db.query(CheckObjectItem).filter(
            CheckObjectItem.check_object_id == check_object.id
        ).delete()

        # Add new items
        for item_data in items_data:
            item = CheckObjectItem(
                check_object_id=check_object.id,
                **item_data
            )
            self.db.add(item)

    def _create_sync_log(
        self,
        sync_type: str,
        status: str,
        fetched_count: int,
        new_count: int,
        updated_count: int,
        error_message: Optional[str]
    ):
        """Create sync log record"""
        log = SyncLog(
            sync_type=sync_type,
            status=status,
            fetched_count=fetched_count,
            new_count=new_count,
            updated_count=updated_count,
            error_message=error_message
        )
        self.db.add(log)
        self.db.commit()

    def get_sync_logs(
        self,
        page: int = 1,
        page_size: int = 20,
        sync_type: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict:
        """
        Get sync logs with pagination and filters

        Args:
            page: Page number
            page_size: Items per page
            sync_type: Filter by sync type
            status: Filter by status

        Returns:
            Dictionary with paginated logs
        """
        query = self.db.query(SyncLog)

        # Apply filters
        if sync_type:
            query = query.filter(SyncLog.sync_type == sync_type)
        if status:
            query = query.filter(SyncLog.status == status)

        # Order by created_at descending
        query = query.order_by(SyncLog.created_at.desc())

        # Get total count
        total = query.count()

        # Apply pagination
        offset = (page - 1) * page_size
        logs = query.offset(offset).limit(page_size).all()

        return {
            "items": logs,
            "total": total,
            "page": page,
            "page_size": page_size
        }
