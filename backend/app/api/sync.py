"""
Sync API Endpoints
T085, T086: Implement sync endpoints
- POST /sync/fetch: Manual trigger
- GET /sync/logs: Sync history with pagination
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.services.sync_service import SyncService
from app.schemas.sync_log import SyncResponse, SyncLogList, SyncLogResponse
from app.models.user import User

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/fetch", response_model=SyncResponse)
def manual_sync(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Trigger manual data synchronization

    Fetches check objects from client API and updates local database.
    Only one sync can run at a time.
    """
    sync_service = SyncService(db)

    try:
        result = sync_service.sync_data(sync_type="manual")

        if result["status"] == "error" and "同步正在进行中" in result.get("message", ""):
            raise HTTPException(
                status_code=400,
                detail="同步正在进行中,请稍后再试"
            )

        return SyncResponse(
            status=result["status"],
            fetched_count=result["fetched_count"],
            new_count=result.get("new_count", 0),
            updated_count=result.get("updated_count", 0),
            message=result["message"]
        )

    except Exception as e:
        if "同步正在进行中" in str(e):
            raise HTTPException(status_code=400, detail=str(e))
        raise HTTPException(status_code=500, detail=f"同步失败: {str(e)}")


@router.get("/logs", response_model=SyncLogList)
def get_sync_logs(
    page: int = 1,
    page_size: int = 20,
    sync_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get sync logs with pagination and filters

    Args:
        page: Page number (default: 1)
        page_size: Items per page (default: 20)
        sync_type: Filter by sync type ("manual" or "auto")
        status: Filter by status ("success" or "error")
    """
    sync_service = SyncService(db)

    result = sync_service.get_sync_logs(
        page=page,
        page_size=page_size,
        sync_type=sync_type,
        status=status
    )

    # Convert models to response format using Pydantic's from_attributes
    items = [SyncLogResponse.model_validate(log) for log in result["items"]]

    return SyncLogList(
        items=items,
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"]
    )
