"""
Reports API Endpoints
T109: POST /reports/upload - Upload PDF report
T110, T111: File size and format validation
T141: GET /reports/download/{check_no} - Download PDF report
T142-T144: POST /reports/export-excel - Export to Excel
"""
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_db, get_current_user
from app.services.file_service import FileService
from app.services.excel_service import ExcelExportService, generate_export_filename
from app.models.user import User
from app.models.check_object import CheckObject

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/upload")
async def upload_report(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload PDF report

    Args:
        file: PDF file to upload (max 10MB)

    Returns:
        file_url: URL to access the uploaded file
        filename: Generated filename
    """
    file_service = FileService()

    try:
        # Validate file size (T110)
        if not file_service.validate_file_size(file, max_size_mb=10):
            raise HTTPException(
                status_code=400,
                detail="文件大小不能超过10MB"
            )

        # Validate PDF format (T111)
        if not file_service.validate_pdf_format(file):
            raise HTTPException(
                status_code=400,
                detail="文件格式必须是PDF"
            )

        # Check if file is empty
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)

        if size == 0:
            raise HTTPException(
                status_code=400,
                detail="文件不能为空"
            )

        # Save file
        result = file_service.save_pdf_report(file, check_no="UPLOAD")

        return {
            "file_url": result["file_url"],
            "filename": result["filename"],
            "message": "文件上传成功"
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@router.get("/download/{check_no}")
async def download_report(
    check_no: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Download PDF report by check_no

    Args:
        check_no: Check object number

    Returns:
        FileResponse with PDF file
    """
    from fastapi.responses import FileResponse
    from app.models.check_object import CheckObject

    # Find check object
    check_object = db.query(CheckObject).filter(
        CheckObject.check_object_union_num == check_no
    ).first()

    if not check_object:
        raise HTTPException(status_code=404, detail="检测对象不存在")

    if not check_object.check_result_url:
        raise HTTPException(status_code=404, detail="报告文件不存在")

    # Convert URL to file path
    file_service = FileService()
    file_path = check_object.check_result_url.replace("/reports/", "")
    full_path = os.path.join(file_service.reports_dir, file_path)

    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="报告文件未找到")

    return FileResponse(
        path=full_path,
        filename=f"{check_no}_report.pdf",
        media_type="application/pdf"
    )


class ExcelExportRequest(BaseModel):
    """Request model for Excel export"""
    check_object_ids: Optional[List[int]] = None
    status: Optional[int] = None
    company: Optional[str] = None
    check_no: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


@router.post("/export-excel")
async def export_excel(
    request: ExcelExportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    T142: Export check results to Excel file
    T143: Validate 1000-row limit
    T144: Apply query filters

    Args:
        request: Export request with IDs or filters

    Returns:
        StreamingResponse with Excel file
    """
    excel_service = ExcelExportService(db)

    try:
        # Get check object IDs to export
        if request.check_object_ids:
            check_object_ids = request.check_object_ids
        else:
            # Build filter query
            filters = {}
            if request.status is not None:
                filters["status"] = request.status
            if request.company:
                filters["company"] = request.company
            if request.check_no:
                filters["check_no"] = request.check_no
            if request.start_date:
                filters["start_date"] = request.start_date
            if request.end_date:
                filters["end_date"] = request.end_date

            # Get IDs from filter query
            query = db.query(CheckObject)

            if filters.get("status") is not None:
                query = query.filter(CheckObject.status == filters["status"])
            if filters.get("company"):
                query = query.filter(
                    CheckObject.submission_person_company.ilike(f"%{filters['company']}%")
                )
            if filters.get("check_no"):
                query = query.filter(CheckObject.check_object_union_num == filters["check_no"])
            if filters.get("start_date"):
                query = query.filter(
                    CheckObject.check_start_time >= filters["start_date"]
                )
            if filters.get("end_date"):
                query = query.filter(
                    CheckObject.check_start_time <= filters["end_date"]
                )

            check_objects = query.all()
            check_object_ids = [obj.id for obj in check_objects]

        # T143: Validate 1000-row limit
        if check_object_ids:
            row_count = excel_service.calculate_row_count(check_object_ids)
            if row_count > 1000:
                raise HTTPException(
                    status_code=400,
                    detail=f"导出数据超过1000行限制,当前数据量: {row_count}行"
                )

        # Check for empty result
        if not check_object_ids:
            raise HTTPException(
                status_code=400,
                detail="没有找到符合条件的数据"
            )

        # Generate Excel file
        excel_bytes = excel_service.export_to_excel(check_object_ids)

        # T146: Generate filename
        filename = generate_export_filename()

        # Return file as streaming response
        return StreamingResponse(
            iter([excel_bytes]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{filename}"
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"导出失败: {str(e)}"
        )
