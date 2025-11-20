"""
Integration test for file upload
Test T102: Test file storage, URL generation
"""
import pytest
from io import BytesIO
import os
from pathlib import Path
from datetime import datetime

from fastapi import UploadFile
from app.services.file_service import FileService


class TestFileUploadIntegration:
    """T102: Integration test for file upload"""

    @pytest.fixture
    def file_service(self):
        return FileService()

    @pytest.fixture
    def test_upload_dir(self, tmp_path):
        """Create temporary upload directory"""
        upload_dir = tmp_path / "uploads" / "reports"
        upload_dir.mkdir(parents=True, exist_ok=True)
        return str(tmp_path / "uploads")

    def test_save_pdf_report_creates_file(self, file_service, test_upload_dir, monkeypatch):
        """Test that saving PDF creates file on disk"""
        monkeypatch.setattr("app.services.file_service.FileService.upload_dir", test_upload_dir)

        pdf_content = b"%PDF-1.4\n%test pdf content"
        fake_file = UploadFile(
            filename="test_report.pdf",
            file=BytesIO(pdf_content)
        )

        result = file_service.save_pdf_report(fake_file, "CHK-001")

        assert result["success"] is True
        assert "file_path" in result
        assert "file_url" in result
        assert os.path.exists(result["file_path"])

    def test_file_path_includes_year_month(self, file_service, test_upload_dir, monkeypatch):
        """Test that file path includes year/month structure"""
        monkeypatch.setattr("app.services.file_service.FileService.upload_dir", test_upload_dir)

        pdf_content = b"%PDF-1.4\n%test"
        fake_file = UploadFile(
            filename="report.pdf",
            file=BytesIO(pdf_content)
        )

        result = file_service.save_pdf_report(fake_file, "CHK-002")

        now = datetime.now()
        expected_path_part = f"/{now.year}/{now.month:02d}/"
        assert expected_path_part in result["file_path"]

    def test_generate_unique_filename(self, file_service):
        """Test that filenames are unique (UUID-based)"""
        filename1 = file_service.generate_filename("report.pdf")
        filename2 = file_service.generate_filename("report.pdf")

        assert filename1 != filename2
        assert filename1.endswith(".pdf")
        assert filename2.endswith(".pdf")

    def test_generate_file_url(self, file_service):
        """Test URL generation"""
        file_path = "/uploads/reports/2024/11/abc123.pdf"
        url = file_service.generate_file_url(file_path)

        assert "/reports/" in url
        assert "2024" in url
        assert "abc123.pdf" in url

    def test_validate_pdf_format_success(self, file_service):
        """Test PDF format validation passes for valid PDF"""
        pdf_content = b"%PDF-1.4\n%test content"
        fake_file = UploadFile(
            filename="test.pdf",
            file=BytesIO(pdf_content)
        )

        is_valid = file_service.validate_pdf_format(fake_file)
        assert is_valid is True

    def test_validate_pdf_format_failure(self, file_service):
        """Test PDF format validation fails for non-PDF"""
        txt_content = b"This is not a PDF"
        fake_file = UploadFile(
            filename="test.txt",
            file=BytesIO(txt_content)
        )

        is_valid = file_service.validate_pdf_format(fake_file)
        assert is_valid is False

    def test_validate_file_size_success(self, file_service):
        """Test file size validation passes for small file"""
        small_content = b"x" * (5 * 1024 * 1024)  # 5MB
        fake_file = UploadFile(
            filename="small.pdf",
            file=BytesIO(small_content)
        )

        is_valid = file_service.validate_file_size(fake_file, max_size_mb=10)
        assert is_valid is True

    def test_validate_file_size_failure(self, file_service):
        """Test file size validation fails for large file"""
        large_content = b"x" * (15 * 1024 * 1024)  # 15MB
        fake_file = UploadFile(
            filename="large.pdf",
            file=BytesIO(large_content)
        )

        is_valid = file_service.validate_file_size(fake_file, max_size_mb=10)
        assert is_valid is False

    def test_directory_creation(self, file_service, test_upload_dir, monkeypatch):
        """Test that directory is created if it doesn't exist"""
        monkeypatch.setattr("app.services.file_service.FileService.upload_dir", test_upload_dir)

        # Directory should not exist yet for current month
        now = datetime.now()
        target_dir = Path(test_upload_dir) / "reports" / str(now.year) / f"{now.month:02d}"

        # Remove if exists
        if target_dir.exists():
            import shutil
            shutil.rmtree(target_dir)

        pdf_content = b"%PDF-1.4\n%test"
        fake_file = UploadFile(
            filename="test.pdf",
            file=BytesIO(pdf_content)
        )

        result = file_service.save_pdf_report(fake_file, "CHK-003")

        # Directory should now exist
        assert target_dir.exists()

    def test_sanitize_filename(self, file_service):
        """Test filename sanitization"""
        dangerous_filename = "../../../etc/passwd.pdf"
        safe_filename = file_service.sanitize_filename(dangerous_filename)

        assert ".." not in safe_filename
        assert "/" not in safe_filename
        assert safe_filename.endswith(".pdf")

    def test_multiple_file_uploads(self, file_service, test_upload_dir, monkeypatch):
        """Test multiple file uploads don't conflict"""
        monkeypatch.setattr("app.services.file_service.FileService.upload_dir", test_upload_dir)

        files = []
        for i in range(3):
            pdf_content = f"%PDF-1.4\n%test {i}".encode()
            fake_file = UploadFile(
                filename=f"report_{i}.pdf",
                file=BytesIO(pdf_content)
            )
            result = file_service.save_pdf_report(fake_file, f"CHK-{i:03d}")
            files.append(result)

        # All files should have unique paths
        paths = [f["file_path"] for f in files]
        assert len(paths) == len(set(paths))

        # All files should exist
        for f in files:
            assert os.path.exists(f["file_path"])
