import shutil
from pathlib import Path
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


def get_disk_usage(path: str = "/") -> Tuple[int, int, int]:
    """
    Get disk usage statistics for a given path.

    Args:
        path: The filesystem path to check

    Returns:
        A tuple of (total_bytes, used_bytes, free_bytes)
    """
    try:
        usage = shutil.disk_usage(path)
        return usage.total, usage.used, usage.free
    except Exception as e:
        logger.error(f"Error getting disk usage for {path}: {e}")
        return 0, 0, 0


def check_storage_space(path: str = "/", threshold_gb: int = 10) -> dict:
    """
    Check if available storage space is below the threshold.

    Args:
        path: The filesystem path to check
        threshold_gb: Alert threshold in GB (default: 10GB)

    Returns:
        A dictionary with storage information and alert status
    """
    total, used, free = get_disk_usage(path)

    # Convert to GB
    total_gb = total / (1024 ** 3)
    used_gb = used / (1024 ** 3)
    free_gb = free / (1024 ** 3)

    # Check if below threshold
    is_low = free_gb < threshold_gb

    result = {
        "path": path,
        "total_gb": round(total_gb, 2),
        "used_gb": round(used_gb, 2),
        "free_gb": round(free_gb, 2),
        "usage_percent": round((used / total * 100), 2) if total > 0 else 0,
        "is_low": is_low,
        "threshold_gb": threshold_gb,
    }

    if is_low:
        logger.warning(
            f"Low storage space alert: {free_gb:.2f}GB free "
            f"(threshold: {threshold_gb}GB) at {path}"
        )

    return result


def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary.

    Args:
        directory_path: The directory path to check/create

    Returns:
        True if directory exists or was created successfully, False otherwise
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory_path}: {e}")
        return False
