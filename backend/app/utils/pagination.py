from typing import Generic, TypeVar, List
from pydantic import BaseModel
from sqlalchemy.orm import Query

T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """通用分页响应模型"""
    total: int
    page: int
    page_size: int
    items: List[T]

    class Config:
        arbitrary_types_allowed = True


def paginate(query: Query, page: int = 1, page_size: int = 50) -> tuple:
    """
    Apply pagination to a SQLAlchemy query.

    Args:
        query: The SQLAlchemy query to paginate
        page: The page number (1-indexed)
        page_size: Number of items per page

    Returns:
        A tuple of (items, total_count)
    """
    # Get total count
    total = query.count()

    # Calculate offset
    offset = (page - 1) * page_size

    # Apply pagination
    items = query.offset(offset).limit(page_size).all()

    return items, total
