"""
Integration tests for Query Filters
Test T155: Test multi-condition filtering and query combinations
"""
import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.models.check_object import CheckObject, CheckObjectItem


class TestQueryFiltersIntegration:
    """T155: Integration test for complex query combinations"""

    def test_status_filter(self, db_session: Session):
        """Test filtering by status"""
        # Create test data with different statuses
        for i in range(3):
            obj = CheckObject(
                check_no=f"STATUS_TEST_{i:03d}",
                sample_name=f"状态测试{i}",
                status=i  # 0, 1, 2
            )
            db_session.add(obj)
        db_session.commit()

        # Query for status=1
        results = db_session.query(CheckObject).filter(
            CheckObject.status == 1,
            CheckObject.check_no.like("STATUS_TEST_%")
        ).all()

        assert len(results) == 1
        assert results[0].status == 1

    def test_company_fuzzy_search(self, db_session: Session):
        """Test fuzzy search on company name"""
        # Create test data
        companies = ["测试科技有限公司", "测试研究院", "其他公司", "科技测试中心"]
        for i, company in enumerate(companies):
            obj = CheckObject(
                check_no=f"COMPANY_TEST_{i:03d}",
                company_name=company,
                status=0
            )
            db_session.add(obj)
        db_session.commit()

        # Fuzzy search for "测试"
        results = db_session.query(CheckObject).filter(
            CheckObject.company_name.ilike("%测试%"),
            CheckObject.check_no.like("COMPANY_TEST_%")
        ).all()

        assert len(results) == 3
        for obj in results:
            assert "测试" in obj.company_name

    def test_check_no_exact_match(self, db_session: Session):
        """Test exact match on check number"""
        # Create test data
        for i in range(5):
            obj = CheckObject(
                check_no=f"EXACT_TEST_{i:03d}",
                sample_name=f"精确测试{i}",
                status=0
            )
            db_session.add(obj)
        db_session.commit()

        # Exact match
        result = db_session.query(CheckObject).filter(
            CheckObject.check_no == "EXACT_TEST_002"
        ).first()

        assert result is not None
        assert result.check_no == "EXACT_TEST_002"
        assert result.sample_name == "精确测试2"

    def test_date_range_filter(self, db_session: Session):
        """Test date range filtering"""
        # Create test data with different dates
        dates = [
            datetime(2024, 1, 1, 10, 0),
            datetime(2024, 2, 15, 14, 0),
            datetime(2024, 3, 30, 16, 0),
            datetime(2024, 5, 20, 9, 0)
        ]

        for i, dt in enumerate(dates):
            obj = CheckObject(
                check_no=f"DATE_TEST_{i:03d}",
                sample_name=f"日期测试{i}",
                sampling_time=dt,
                status=0
            )
            db_session.add(obj)
        db_session.commit()

        # Query for February to March
        start = date(2024, 2, 1)
        end = date(2024, 3, 31)

        results = db_session.query(CheckObject).filter(
            CheckObject.check_no.like("DATE_TEST_%"),
            CheckObject.sampling_time >= start,
            CheckObject.sampling_time <= datetime.combine(end, datetime.max.time())
        ).all()

        assert len(results) == 2
        assert all(result.check_no in ["DATE_TEST_001", "DATE_TEST_002"] for result in results)

    def test_combined_filters(self, db_session: Session):
        """Test combination of multiple filters"""
        # Create test data
        test_data = [
            ("COMBO_001", "测试公司A", 0, datetime(2024, 1, 10)),
            ("COMBO_002", "测试公司A", 1, datetime(2024, 1, 20)),
            ("COMBO_003", "测试公司B", 0, datetime(2024, 1, 15)),
            ("COMBO_004", "测试公司A", 0, datetime(2024, 2, 5)),
            ("COMBO_005", "其他公司", 0, datetime(2024, 1, 15)),
        ]

        for check_no, company, status, sampling_time in test_data:
            obj = CheckObject(
                check_no=check_no,
                company_name=company,
                status=status,
                sampling_time=sampling_time
            )
            db_session.add(obj)
        db_session.commit()

        # Query: company LIKE "测试公司A" AND status=0 AND date in Jan
        start = date(2024, 1, 1)
        end = date(2024, 1, 31)

        results = db_session.query(CheckObject).filter(
            CheckObject.check_no.like("COMBO_%"),
            CheckObject.company_name.ilike("%测试公司A%"),
            CheckObject.status == 0,
            CheckObject.sampling_time >= start,
            CheckObject.sampling_time <= datetime.combine(end, datetime.max.time())
        ).all()

        assert len(results) == 1
        assert results[0].check_no == "COMBO_001"

    def test_empty_results(self, db_session: Session):
        """Test that empty filters return all data"""
        # Create test data
        for i in range(5):
            obj = CheckObject(
                check_no=f"EMPTY_TEST_{i:03d}",
                sample_name=f"空测试{i}",
                status=i % 3
            )
            db_session.add(obj)
        db_session.commit()

        # Query without filters
        results = db_session.query(CheckObject).filter(
            CheckObject.check_no.like("EMPTY_TEST_%")
        ).all()

        assert len(results) == 5

    def test_no_matches(self, db_session: Session):
        """Test query with no matching results"""
        # Create test data
        obj = CheckObject(
            check_no="NOMATCH_001",
            company_name="测试公司",
            status=0
        )
        db_session.add(obj)
        db_session.commit()

        # Query for non-existent data
        results = db_session.query(CheckObject).filter(
            CheckObject.check_no == "NONEXISTENT"
        ).all()

        assert len(results) == 0

    def test_pagination_with_filters(self, db_session: Session):
        """Test pagination works correctly with filters"""
        # Create 25 records
        for i in range(25):
            obj = CheckObject(
                check_no=f"PAGE_TEST_{i:03d}",
                company_name="测试公司" if i % 2 == 0 else "其他公司",
                status=0
            )
            db_session.add(obj)
        db_session.commit()

        # Query with filter and pagination
        query = db_session.query(CheckObject).filter(
            CheckObject.check_no.like("PAGE_TEST_%"),
            CheckObject.company_name == "测试公司"
        )

        total = query.count()
        assert total == 13  # Half of 25, rounded up

        # Page 1
        page1 = query.offset(0).limit(10).all()
        assert len(page1) == 10

        # Page 2
        page2 = query.offset(10).limit(10).all()
        assert len(page2) == 3

    def test_order_by_with_filters(self, db_session: Session):
        """Test that ordering works with filters"""
        # Create test data
        for i in range(5):
            obj = CheckObject(
                check_no=f"ORDER_TEST_{i:03d}",
                company_name="测试公司",
                status=0,
                created_at=datetime(2024, 1, i + 1)
            )
            db_session.add(obj)
        db_session.commit()

        # Query with filter and order
        results = db_session.query(CheckObject).filter(
            CheckObject.check_no.like("ORDER_TEST_%")
        ).order_by(CheckObject.created_at.desc()).all()

        assert len(results) == 5
        assert results[0].check_no == "ORDER_TEST_004"
        assert results[4].check_no == "ORDER_TEST_000"

    def test_case_insensitive_company_search(self, db_session: Session):
        """Test that company search is case-insensitive"""
        # Create test data
        obj = CheckObject(
            check_no="CASE_TEST_001",
            company_name="Beijing Test Company",
            status=0
        )
        db_session.add(obj)
        db_session.commit()

        # Search with different cases
        for search_term in ["beijing", "BEIJING", "BeIjInG"]:
            results = db_session.query(CheckObject).filter(
                CheckObject.company_name.ilike(f"%{search_term}%")
            ).all()

            assert len(results) >= 1

    def test_partial_date_range(self, db_session: Session):
        """Test date range with only start or end date"""
        # Create test data
        dates = [
            datetime(2024, 1, 1),
            datetime(2024, 2, 1),
            datetime(2024, 3, 1)
        ]

        for i, dt in enumerate(dates):
            obj = CheckObject(
                check_no=f"PARTIAL_DATE_{i:03d}",
                sampling_time=dt,
                status=0
            )
            db_session.add(obj)
        db_session.commit()

        # Only start date
        results = db_session.query(CheckObject).filter(
            CheckObject.check_no.like("PARTIAL_DATE_%"),
            CheckObject.sampling_time >= date(2024, 2, 1)
        ).all()

        assert len(results) == 2

        # Only end date
        results = db_session.query(CheckObject).filter(
            CheckObject.check_no.like("PARTIAL_DATE_%"),
            CheckObject.sampling_time <= datetime.combine(date(2024, 2, 1), datetime.max.time())
        ).all()

        assert len(results) == 2

    def test_filter_performance(self, db_session: Session):
        """Test that filters don't cause performance issues"""
        import time

        # Create 100 records
        for i in range(100):
            obj = CheckObject(
                check_no=f"PERF_TEST_{i:04d}",
                company_name=f"公司{i % 10}",
                status=i % 3,
                sampling_time=datetime(2024, (i % 12) + 1, 1)
            )
            db_session.add(obj)
        db_session.commit()

        # Measure query time
        start = time.time()

        results = db_session.query(CheckObject).filter(
            CheckObject.check_no.like("PERF_TEST_%"),
            CheckObject.company_name.ilike("%公司5%"),
            CheckObject.status == 1
        ).all()

        elapsed = time.time() - start

        # Query should complete in less than 1 second
        assert elapsed < 1.0
        assert len(results) > 0
