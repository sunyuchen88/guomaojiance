"""
Reports API Endpoints
T109: POST /reports/upload - Upload PDF report
T110, T111: File size and format validation
T141: GET /reports/download/{check_no} - Download PDF report
T142-T144: POST /reports/export-excel - Export to Excel
需求2.4: POST /reports/batch-download - Batch download PDF reports
"""
import os
import io
import zipfile
import logging
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.api.deps import get_db, get_current_user
from app.services.file_service import FileService
from app.services.excel_service import ExcelExportService, generate_export_filename
from app.models.user import User
from app.models.check_object import CheckObject

logger = logging.getLogger(__name__)

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


class BatchDownloadRequest(BaseModel):
    """
    需求2.4: Request model for batch PDF download
    支持多维度筛选后批量下载报告
    """
    status: Optional[int] = None
    company: Optional[str] = None
    check_no: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    check_result: Optional[str] = None


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

        # URL encode filename for Content-Disposition header
        from urllib.parse import quote
        encoded_filename = quote(filename)

        # Return file as streaming response
        return StreamingResponse(
            iter([excel_bytes]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Export Excel failed: {str(e)}\n{error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"导出失败: {str(e)}"
        )


@router.post("/batch-download")
async def batch_download_reports(
    request: BatchDownloadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    需求2.4: 批量下载检测报告PDF
    支持多维度筛选后批量下载所有匹配的报告

    Args:
        request: 筛选条件
            - status: 状态筛选
            - company: 公司名称筛选
            - check_no: 检测编号筛选
            - start_date: 采样起始时间
            - end_date: 采样结束时间
            - check_result: 检测结果筛选（合格/不合格）

    Returns:
        StreamingResponse with ZIP file containing all matched PDF reports
    """
    file_service = FileService()

    try:
        # Build filter query
        query = db.query(CheckObject)

        # Apply filters (same as check_objects list endpoint)
        if request.status is not None:
            query = query.filter(CheckObject.status == request.status)

        if request.company:
            query = query.filter(
                CheckObject.submission_person_company.ilike(f"%{request.company}%")
            )

        if request.check_no:
            query = query.filter(
                CheckObject.check_object_union_num == request.check_no
            )

        if request.start_date:
            query = query.filter(CheckObject.check_start_time >= request.start_date)

        if request.end_date:
            from datetime import datetime, timedelta
            end_datetime = datetime.combine(request.end_date, datetime.max.time())
            query = query.filter(CheckObject.check_start_time <= end_datetime)

        if request.check_result:
            query = query.filter(CheckObject.check_result == request.check_result)

        # Get all matching check objects
        check_objects = query.all()

        if not check_objects:
            raise HTTPException(
                status_code=404,
                detail="没有找到符合条件的检测报告"
            )

        # Collect all PDF files
        pdf_files = []
        for obj in check_objects:
            if obj.check_result_url:
                # Convert URL to file path
                file_path = obj.check_result_url.replace("/reports/", "")
                full_path = os.path.join(file_service.reports_dir, file_path)

                if os.path.exists(full_path):
                    pdf_files.append({
                        "path": full_path,
                        "filename": f"{obj.check_object_union_num}_report.pdf"
                    })

        if not pdf_files:
            # Count objects without URL
            no_url_count = sum(1 for obj in check_objects if not obj.check_result_url)
            raise HTTPException(
                status_code=404,
                detail=f"没有找到可下载的报告文件。共{len(check_objects)}个检测对象，{no_url_count}个未上传报告"
            )

        # Create ZIP file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for pdf_info in pdf_files:
                zip_file.write(pdf_info["path"], pdf_info["filename"])

        zip_buffer.seek(0)

        # Generate filename with timestamp
        from datetime import datetime
        from urllib.parse import quote
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"reports_batch_{timestamp}.zip"
        encoded_zip_filename = quote(zip_filename)

        # Return ZIP file
        return StreamingResponse(
            iter([zip_buffer.getvalue()]),
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_zip_filename}"
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Batch download failed: {str(e)}\n{error_trace}")
        raise HTTPException(
            status_code=500,
            detail=f"批量下载失败: {str(e)}"
        )
