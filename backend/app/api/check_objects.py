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
        query = query.filter(CheckObject.company_name.ilike(f"%{company}%"))

    if check_no:
        # Exact match on check number
        query = query.filter(CheckObject.check_no == check_no)

    if start_date:
        query = query.filter(CheckObject.sampling_time >= start_date)

    if end_date:
        # Include the entire end_date
        from datetime import datetime, timedelta
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.filter(CheckObject.sampling_time <= end_datetime)

    # Order by created_at descending
    query = query.order_by(CheckObject.created_at.desc())

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    check_objects = query.offset(offset).limit(page_size).all()

    # Convert to response format
    items = [
        CheckObjectResponse(
            id=obj.id,
            check_no=obj.check_no,
            sample_name=obj.sample_name,
            company_name=obj.company_name,
            status=obj.status,
            sampling_time=obj.sampling_time,
            check_result=obj.check_result,
            report_url=obj.report_url,
            created_at=obj.created_at,
            updated_at=obj.updated_at
        )
        for obj in check_objects
    ]

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

    # Convert check items to response format
    check_items = [
        CheckObjectItemResponse(
            id=item.id,
            check_item_name=item.check_item_name,
            check_method=item.check_method,
            standard_value=item.standard_value,
            check_result=item.check_result,
            result_indicator=item.result_indicator
        )
        for item in check_object.check_items
    ]

    return CheckObjectDetailResponse(
        id=check_object.id,
        check_no=check_object.check_no,
        sample_name=check_object.sample_name,
        company_name=check_object.company_name,
        sample_source=check_object.sample_source,
        sample_base_num=check_object.sample_base_num,
        product_date=check_object.product_date,
        specs=check_object.specs,
        grade=check_object.grade,
        executive_standards=check_object.executive_standards,
        production_license_num=check_object.production_license_num,
        sampling_num=check_object.sampling_num,
        sampling_site=check_object.sampling_site,
        sampling_address=check_object.sampling_address,
        sampling_time=check_object.sampling_time,
        commissioning_unit=check_object.commissioning_unit,
        is_subcontract=check_object.is_subcontract,
        subcontract_lab=check_object.subcontract_lab,
        status=check_object.status,
        check_result=check_object.check_result,
        report_url=check_object.report_url,
        remark=check_object.remark,
        check_items=check_items,
        created_at=check_object.created_at,
        updated_at=check_object.updated_at
    )


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
    T108: Update check result and set status to 1

    Args:
        check_object_id: ID of the check object
        result_data: {
            "check_result": str,  # Overall result
            "check_items": [{id, check_result, result_indicator}, ...]
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

    # Update check items if provided
    if "check_items" in result_data and result_data["check_items"]:
        for item_data in result_data["check_items"]:
            item_id = item_data.get("id")
            if item_id:
                item = db.query(CheckObjectItem).filter(
                    CheckObjectItem.id == item_id,
                    CheckObjectItem.check_object_id == check_object_id
                ).first()

                if item:
                    if "check_result" in item_data:
                        item.check_result = item_data["check_result"]
                    if "result_indicator" in item_data:
                        item.result_indicator = item_data["result_indicator"]

    db.commit()
    db.refresh(check_object)

    # Return updated detail
    return get_check_object_detail(check_object_id, db, current_user)

