"""
Unit tests for File Service
Test T103: Test path generation, storage logic
"""
import pytest
from pathlib import Path
from datetime import datetime
import os

from app.services.file_service import FileService


class TestFileService:
    """T103: Unit test for file service"""

    @pytest.fixture
    def file_service(self):
        return FileService()

    def test_generate_filename_with_uuid(self, file_service):
        """Test filename generation includes UUID"""
        filename = file_service.generate_filename("test.pdf")

        assert filename.endswith(".pdf")
        assert len(filename) > len("test.pdf")  # Should include UUID
        # UUID format: 8-4-4-4-12 characters
        assert filename.count("-") >= 4  # UUID has 4 dashes

    def test_generate_filename_preserves_extension(self, file_service):
        """Test that file extension is preserved"""
        filenames = [
            "report.pdf",
            "test.PDF",
            "document.Pdf"
        ]

        for original in filenames:
            generated = file_service.generate_filename(original)
            assert generated.lower().endswith(".pdf")

    def test_generate_file_path(self, file_service):
        """Test file path generation with year/month structure"""
        filename = "test_report.pdf"
        check_no = "CHK-001"

        file_path = file_service.generate_file_path(filename, check_no)

        # Should contain year
        now = datetime.now()
        assert str(now.year) in file_path

        # Should contain month
        assert f"{now.month:02d}" in file_path

        # Should contain filename
        assert filename in file_path

    def test_generate_file_url_format(self, file_service):
        """Test URL generation format"""
        file_path = "/uploads/reports/2024/11/abc-123.pdf"
        url = file_service.generate_file_url(file_path)

        # Should start with /reports/ or http://
        assert url.startswith("/reports/") or url.startswith("http")

        # Should contain year and month
        assert "2024" in url
        assert "11" in url

        # Should contain filename
        assert "abc-123.pdf" in url

    def test_sanitize_filename_removes_path_traversal(self, file_service):
        """Test filename sanitization removes path traversal"""
        dangerous_names = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "test/../../../file.pdf"
        ]

        for dangerous in dangerous_names:
            safe = file_service.sanitize_filename(dangerous)
            assert ".." not in safe
            assert "/" not in safe or safe.startswith("/")
            assert "\\" not in safe

    def test_sanitize_filename_handles_special_chars(self, file_service):
        """Test filename sanitization handles special characters"""
        names_with_special_chars = [
            "报告 测试.pdf",
            "test<script>.pdf",
            "file:name.pdf",
            "test|file.pdf"
        ]

        for name in names_with_special_chars:
            safe = file_service.sanitize_filename(name)
            assert safe.endswith(".pdf")
            # Should not contain dangerous characters
            dangerous_chars = ["<", ">", ":", "|", "?", "*"]
            for char in dangerous_chars:
                assert char not in safe

    def test_get_file_size_mb(self, file_service, tmp_path):
        """Test file size calculation"""
        # Create a test file
        test_file = tmp_path / "test.pdf"
        content = b"x" * (5 * 1024 * 1024)  # 5MB
        test_file.write_bytes(content)

        size_mb = file_service.get_file_size_mb(str(test_file))

        assert 4.9 < size_mb < 5.1  # Allow small variance

    def test_validate_pdf_extension(self, file_service):
        """Test PDF extension validation"""
        valid_extensions = ["test.pdf", "TEST.PDF", "Report.Pdf"]
        invalid_extensions = ["test.txt", "file.doc", "image.png"]

        for filename in valid_extensions:
            assert file_service.validate_pdf_extension(filename) is True

        for filename in invalid_extensions:
            assert file_service.validate_pdf_extension(filename) is False

    def test_create_directory_structure(self, file_service, tmp_path):
        """Test directory creation"""
        target_dir = tmp_path / "test" / "2024" / "11"

        file_service.ensure_directory_exists(str(target_dir))

        assert target_dir.exists()
        assert target_dir.is_dir()

    def test_get_storage_path(self, file_service):
        """Test storage path calculation"""
        check_no = "CHK-2024-001"
        filename = "report.pdf"

        storage_path = file_service.get_storage_path(check_no, filename)

        # Should include uploads directory
        assert "uploads" in storage_path or "reports" in storage_path

        # Should include year/month
        now = datetime.now()
        assert str(now.year) in storage_path

    def test_is_pdf_by_magic_number(self, file_service):
        """Test PDF detection by magic number"""
        pdf_content = b"%PDF-1.4\ntest content"
        not_pdf_content = b"This is not a PDF"

        assert file_service.is_pdf_by_magic_number(pdf_content) is True
        assert file_service.is_pdf_by_magic_number(not_pdf_content) is False

    def test_generate_download_url(self, file_service):
        """Test download URL generation"""
        check_no = "CHK-001"
        url = file_service.generate_download_url(check_no)

        assert "/reports/download/" in url or check_no in url

    def test_file_path_is_absolute(self, file_service):
        """Test that generated file paths are absolute"""
        filename = "test.pdf"
        check_no = "CHK-001"

        file_path = file_service.generate_file_path(filename, check_no)

        # Should be absolute path
        assert os.path.isabs(file_path) or file_path.startswith("/")
