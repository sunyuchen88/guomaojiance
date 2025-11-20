"""
File Service
T106: Implement FileService
- save_pdf_report: Save PDF to disk
- generate_file_path: Generate storage path
- generate_url: Generate access URL
"""
import os
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from fastapi import UploadFile

from app.config import settings


class FileService:
    """Service for handling file uploads and storage"""

    def __init__(self):
        self.upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
        self.reports_dir = os.path.join(self.upload_dir, "reports")
        self.max_file_size_mb = 10

    def save_pdf_report(
        self,
        file: UploadFile,
        check_no: str
    ) -> Dict:
        """
        Save PDF report to disk

        Args:
            file: Uploaded file
            check_no: Check object number

        Returns:
            Dictionary with file path and URL

        Raises:
            ValueError: If file validation fails
        """
        # Validate file
        if not self.validate_pdf_format(file):
            raise ValueError("文件格式必须是PDF")

        if not self.validate_file_size(file, self.max_file_size_mb):
            raise ValueError(f"文件大小不能超过{self.max_file_size_mb}MB")

        # Generate filename
        safe_filename = self.sanitize_filename(file.filename)
        unique_filename = self.generate_filename(safe_filename)

        # Generate file path with year/month structure
        now = datetime.now()
        year = now.year
        month = f"{now.month:02d}"

        target_dir = Path(self.reports_dir) / str(year) / month
        self.ensure_directory_exists(str(target_dir))

        file_path = target_dir / unique_filename

        # Save file
        try:
            content = file.file.read()
            with open(file_path, "wb") as f:
                f.write(content)

            # Generate URL
            file_url = self.generate_file_url(str(file_path))

            return {
                "success": True,
                "file_path": str(file_path),
                "file_url": file_url,
                "filename": unique_filename
            }

        except Exception as e:
            raise Exception(f"保存文件失败: {str(e)}")

        finally:
            file.file.seek(0)  # Reset file pointer

    def generate_filename(self, original_filename: str) -> str:
        """Generate unique filename with UUID"""
        ext = Path(original_filename).suffix.lower()
        if not ext:
            ext = ".pdf"

        unique_id = str(uuid.uuid4())
        return f"{unique_id}{ext}"

    def generate_file_path(self, filename: str, check_no: str) -> str:
        """Generate file path with year/month structure"""
        now = datetime.now()
        year = now.year
        month = f"{now.month:02d}"

        path = os.path.join(
            self.reports_dir,
            str(year),
            month,
            filename
        )

        return path

    def generate_file_url(self, file_path: str) -> str:
        """
        Generate accessible URL for file

        Args:
            file_path: Absolute file path

        Returns:
            URL path for accessing file
        """
        # Extract relative path from reports directory
        file_path = file_path.replace("\\", "/")

        if "/reports/" in file_path:
            # Extract everything after /reports/
            relative_path = file_path.split("/reports/")[-1]
            return f"/reports/{relative_path}"
        else:
            # Fallback: use filename
            filename = os.path.basename(file_path)
            return f"/reports/{filename}"

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        # Remove path components
        filename = os.path.basename(filename)

        # Remove dangerous characters
        dangerous_chars = ["<", ">", ":", "\"", "|", "?", "*", "\\"]
        for char in dangerous_chars:
            filename = filename.replace(char, "_")

        # Ensure it's not empty
        if not filename:
            filename = "report.pdf"

        return filename

    def validate_pdf_format(self, file: UploadFile) -> bool:
        """
        Validate that file is PDF format

        Args:
            file: Uploaded file

        Returns:
            True if valid PDF, False otherwise
        """
        # Check extension
        if not file.filename.lower().endswith(".pdf"):
            return False

        # Check content type
        if file.content_type and "pdf" not in file.content_type.lower():
            return False

        # Check magic number
        try:
            content = file.file.read(1024)  # Read first 1KB
            file.file.seek(0)  # Reset

            # PDF files start with %PDF
            if content.startswith(b"%PDF"):
                return True

        except:
            file.file.seek(0)

        return False

    def validate_pdf_extension(self, filename: str) -> bool:
        """Validate PDF file extension"""
        return filename.lower().endswith(".pdf")

    def validate_file_size(self, file: UploadFile, max_size_mb: int) -> bool:
        """
        Validate file size

        Args:
            file: Uploaded file
            max_size_mb: Maximum size in MB

        Returns:
            True if size is valid, False otherwise
        """
        try:
            # Get file size
            file.file.seek(0, 2)  # Seek to end
            size_bytes = file.file.tell()
            file.file.seek(0)  # Reset

            max_size_bytes = max_size_mb * 1024 * 1024

            return size_bytes <= max_size_bytes and size_bytes > 0

        except:
            file.file.seek(0)
            return False

    def ensure_directory_exists(self, directory: str):
        """Create directory if it doesn't exist"""
        Path(directory).mkdir(parents=True, exist_ok=True)

    def get_file_size_mb(self, file_path: str) -> float:
        """Get file size in MB"""
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)

    def is_pdf_by_magic_number(self, content: bytes) -> bool:
        """Check if content is PDF by magic number"""
        return content.startswith(b"%PDF")

    def get_storage_path(self, check_no: str, filename: str) -> str:
        """Get storage path for a file"""
        return self.generate_file_path(filename, check_no)

    def generate_download_url(self, check_no: str) -> str:
        """Generate download URL for check_no"""
        return f"/api/reports/download/{check_no}"
