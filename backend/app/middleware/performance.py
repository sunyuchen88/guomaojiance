import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log request processing time and identify slow requests.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request and log response time.

        Args:
            request: The incoming request
            call_next: The next middleware or route handler

        Returns:
            The response from the route handler
        """
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time
        process_time_ms = round(process_time * 1000, 2)

        # Add custom header
        response.headers["X-Process-Time"] = str(process_time_ms)

        # Log slow requests (>500ms)
        if process_time_ms > 500:
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path} "
                f"took {process_time_ms}ms"
            )
        else:
            logger.info(
                f"{request.method} {request.url.path} "
                f"completed in {process_time_ms}ms"
            )

        return response
