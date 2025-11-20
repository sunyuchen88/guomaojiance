from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

from app.config import settings
from app.middleware.performance import PerformanceMiddleware
from app.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    database_exception_handler,
    general_exception_handler,
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="食品质检系统 API",
    description="国贸食品科学研究院检测系统后端API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(PerformanceMiddleware)

# Register exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Mount static files for report downloads
# T112: Configure static file serving
import os
reports_dir = os.path.join(os.path.dirname(__file__), "uploads", "reports")
if os.path.exists(reports_dir):
    app.mount("/reports", StaticFiles(directory=reports_dir), name="reports")


# API routes
from app.api import auth, sync, check_objects, reports, submit

app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(sync.router, prefix="/api/v1", tags=["Data Sync"])
app.include_router(check_objects.router, prefix="/api/v1", tags=["Check Objects"])
app.include_router(reports.router, prefix="/api/v1", tags=["Reports"])
app.include_router(submit.router, prefix="/api/v1", tags=["Submit Results"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "食品质检系统 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup tasks"""
    logger.info("Starting 食品质检系统 API...")
    # Start APScheduler
    from app.tasks.scheduler import start_scheduler
    start_scheduler()


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown tasks"""
    logger.info("Shutting down 食品质检系统 API...")
    # Stop APScheduler
    from app.tasks.scheduler import shutdown_scheduler
    shutdown_scheduler()
