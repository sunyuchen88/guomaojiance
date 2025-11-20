"""
Submit API Endpoint
T126, T127: POST /submit/{check_object_id}
- Call SubmitService
- Update status to 2
- Handle errors
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.services.submit_service import SubmitService
from app.models.user import User

router = APIRouter(prefix="/submit", tags=["submit"])


@router.post("/{check_object_id}")
def submit_check_result(
    check_object_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit check result to client API
    T126: Validate status=1, call SubmitService, update status to 2

    Args:
        check_object_id: ID of check object to submit

    Returns:
        Success message or error
    """
    submit_service = SubmitService(db)

    try:
        result = submit_service.submit_check_object(check_object_id)

        if not result["success"]:
            # T127: Return error with client error message
            raise HTTPException(
                status_code=400,
                detail=result["message"]
            )

        return {
            "success": True,
            "message": result["message"],
            "check_object_id": check_object_id
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"提交失败: {str(e)}"
        )
