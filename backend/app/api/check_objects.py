"""
Check Objects API Endpoints
T087, T088, T089: Implement check-objects endpoints
- GET /check-objects: Query filters, pagination
- GET /check-objects/{id}: Detail retrieval
- PUT /check-objects/{id}: Update sample info
"""
from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.check_object import CheckObject
from app.models.check_item import CheckObjectItem
from app.schemas.check_object import (
    CheckObjectList,
    CheckObjectResponse,
    CheckObjectDetailResponse,
    CheckObjectUpdate,
    CheckObjectItemResponse
)

router = APIRouter(prefix="/check-objects", tags=["check-objects"])


@router.get("", response_model=CheckObjectList)
def get_check_objects(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[int] = None,
    company: Optional[str] = None,
    check_no: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get check objects with filters and pagination

    Args:
        page: Page number (default: 1)
        page_size: Items per page (default: 10, max: 100)
        status: Filter by status (0=待检测, 1=已检测, 2=已提交)
        company: Filter by company name (fuzzy search)
        check_no: Filter by check number (exact match)
        start_date: Filter by sampling date start
        end_date: Filter by sampling date end
    """
    query = db.query(CheckObject)

    # Apply filters
    if status is not None:
        query = query.filter(CheckObject.status == status)

    if company:
        # Fuzzy search on company name
        query = query.filter(CheckObject.submission_person_company.ilike(f"%{company}%"))

    if check_no:
        # Exact match on check number
        query = query.filter(CheckObject.check_object_union_num == check_no)

    if start_date:
        query = query.filter(CheckObject.check_start_time >= start_date)

    if end_date:
        # Include the entire end_date
        from datetime import datetime, timedelta
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.filter(CheckObject.check_start_time <= end_datetime)

    # Order by create_time descending
    query = query.order_by(CheckObject.create_time.desc())

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    check_objects = query.offset(offset).limit(page_size).all()

    # Convert to response format using Pydantic's from_attributes
    items = [CheckObjectResponse.model_validate(obj) for obj in check_objects]

    return CheckObjectList(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{check_object_id}", response_model=CheckObjectDetailResponse)
def get_check_object_detail(
    check_object_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get check object detail with check items

    Args:
        check_object_id: ID of the check object
    """
    # Query with eager loading of check items
    check_object = db.query(CheckObject).options(
        joinedload(CheckObject.check_items)
    ).filter(
        CheckObject.id == check_object_id
    ).first()

    if not check_object:
        raise HTTPException(status_code=404, detail="检测对象不存在")

    # Convert check items to response format using Pydantic's from_attributes
    check_items = [CheckObjectItemResponse.model_validate(item) for item in check_object.check_items]

    # Convert check object to response format
    response_data = CheckObjectDetailResponse.model_validate(check_object)
    response_data.check_items = check_items

    return response_data


@router.put("/{check_object_id}", response_model=CheckObjectDetailResponse)
def update_check_object(
    check_object_id: int,
    update_data: CheckObjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update check object and its check items

    Args:
        check_object_id: ID of the check object
        update_data: Fields to update
    """
    # Query the check object
    check_object = db.query(CheckObject).filter(
        CheckObject.id == check_object_id
    ).first()

    if not check_object:
        raise HTTPException(status_code=404, detail="检测对象不存在")

    # Validate status if provided
    if update_data.status is not None and update_data.status not in [0, 1, 2]:
        raise HTTPException(status_code=422, detail="无效的状态值")

    # Update check object fields
    update_dict = update_data.dict(exclude_unset=True, exclude={"check_items"})
    for key, value in update_dict.items():
        setattr(check_object, key, value)

    # Update check items if provided
    if update_data.check_items is not None:
        for item_update in update_data.check_items:
            if item_update.id:
                # Update existing item
                item = db.query(CheckObjectItem).filter(
                    CheckObjectItem.id == item_update.id,
                    CheckObjectItem.check_object_id == check_object_id
                ).first()

                if item:
                    for key, value in item_update.dict(exclude_unset=True).items():
                        if key != "id":
                            setattr(item, key, value)

    db.commit()
    db.refresh(check_object)

    # Return updated detail
    return get_check_object_detail(check_object_id, db, current_user)


@router.put("/{check_object_id}/result", response_model=CheckObjectDetailResponse)
def input_check_result(
    check_object_id: int,
    result_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Input check result for a check object
    T108, T2.2: Update check result with 5 core fields and set status to 1

    Args:
        check_object_id: ID of the check object
        result_data: {
            "check_result": str,  # Overall result
            "check_items": [{
                id,
                check_item_name,    # 检测项目
                check_method,       # 检测方法
                unit,               # 单位
                num,                # 检测结果
                detection_limit,    # 检出限
                result              # 结果判定
            }, ...]
        }
    """
    # Query the check object
    check_object = db.query(CheckObject).filter(
        CheckObject.id == check_object_id
    ).first()

    if not check_object:
        raise HTTPException(status_code=404, detail="检测对象不存在")

    # Prevent modification of already submitted results
    if check_object.status == 2:
        raise HTTPException(status_code=400, detail="已提交的检测对象不能修改结果")

    # Validate check_result is provided
    if "check_result" not in result_data:
        raise HTTPException(status_code=422, detail="检验结果不能为空")

    # Update overall check result
    check_object.check_result = result_data["check_result"]

    # Update status to 1 (已检测)
    check_object.status = 1

    # Update check items if provided - T2.2: Support 5 core fields
    if "check_items" in result_data and result_data["check_items"]:
        for item_data in result_data["check_items"]:
            item_id = item_data.get("id")
            if item_id:
                item = db.query(CheckObjectItem).filter(
                    CheckObjectItem.id == item_id,
                    CheckObjectItem.check_object_id == check_object.check_object_id
                ).first()

                if item:
                    # T2.2: Update 5 core fields
                    if "check_item_name" in item_data:
                        item.check_item_name = item_data["check_item_name"]
                    if "check_method" in item_data:
                        item.check_method = item_data["check_method"]
                    if "unit" in item_data:
                        item.unit = item_data["unit"]
                    if "num" in item_data:
                        item.num = item_data["num"]
                    if "detection_limit" in item_data:
                        item.detection_limit = item_data["detection_limit"]
                    if "result" in item_data:
                        item.result = item_data["result"]

    db.commit()
    db.refresh(check_object)

    # Return updated detail
    return get_check_object_detail(check_object_id, db, current_user)

