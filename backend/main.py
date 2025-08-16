import argparse
import logging
import os
import signal
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

import psutil

import requests
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from data_service import DataService
from models import (
    TimelineResponse, ItemsResponse, AppDayData,
    HealthResponse, PaginatedResponse
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Signal handlers for graceful shutdown and OOM detection
def signal_handler(signum, frame):
    """Handle various signals that may indicate process termination"""
    signal_names = {
        signal.SIGTERM: "SIGTERM (graceful termination)",
        signal.SIGINT: "SIGINT (interrupt)",
        signal.SIGQUIT: "SIGQUIT (quit)",
        signal.SIGUSR1: "SIGUSR1 (user signal 1)",
        signal.SIGUSR2: "SIGUSR2 (user signal 2)",
    }

    signal_name = signal_names.get(signum, f"Signal {signum}")
    logger.warning(f"Received {signal_name} - Application may be shutting down due to system constraints (possible OOM or external termination)")

    # For SIGTERM and SIGINT, exit gracefully
    if signum in [signal.SIGTERM, signal.SIGINT]:
        logger.info("Initiating graceful shutdown...")
        sys.exit(0)


# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGQUIT, signal_handler)
# Note: SIGKILL cannot be caught, but we can catch other signals that might indicate resource issues
signal.signal(signal.SIGUSR1, signal_handler)
signal.signal(signal.SIGUSR2, signal_handler)

# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Awesome Crawler Backend API')
    parser.add_argument('--local-file', type=str, help='Use local file instead of S3 (overrides env vars)')
    return parser.parse_args()

# Initialize configuration - only parse args if running directly
if __name__ == "__main__":
    args = parse_args()
    if args.local_file:
        DATA_SOURCE = "local"
        LOCAL_FILE_PATH = args.local_file
        S3_BUCKET = None
        S3_KEY = None
    else:
        DATA_SOURCE = "s3"
        S3_BUCKET = os.getenv("S3_BUCKET", "awesome-crawler.allocsoc.net")
        S3_KEY = os.getenv("S3_KEY", "data.json")
        LOCAL_FILE_PATH = None
else:
    # When imported by uvicorn, use environment variables only
    DATA_SOURCE = os.getenv("DATA_SOURCE", "s3")
    S3_BUCKET = os.getenv("S3_BUCKET", "awesome-crawler.allocsoc.net")
    S3_KEY = os.getenv("S3_KEY", "data.json")
    LOCAL_FILE_PATH = os.getenv("LOCAL_FILE_PATH", "data/data.json")

data_service = DataService(
    data_source=DATA_SOURCE,
    bucket_name=S3_BUCKET,
    s3_key=S3_KEY,
    local_file_path=LOCAL_FILE_PATH
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting awesome-crawler backend...")

    process = psutil.Process()
    memory_info = process.memory_info()
    logger.info(f"Initial memory usage: RSS={memory_info.rss / 1024 / 1024:.1f}MB, VMS={memory_info.vms / 1024 / 1024:.1f}MB")

    # Load initial data from configured source
    logger.info(f"Loading data from {DATA_SOURCE.upper()} source")
    success = data_service.load_data()
    if not success:
        logger.warning(f"Failed to load initial data from {DATA_SOURCE.upper()}")

    memory_info = process.memory_info()
    logger.info(f"Memory usage after data loading: RSS={memory_info.rss / 1024 / 1024:.1f}MB, VMS={memory_info.vms / 1024 / 1024:.1f}MB")

    yield

    # Shutdown
    logger.info("Shutting down awesome-crawler backend...")


# Create FastAPI app
app = FastAPI(
    title="Awesome Crawler API",
    description="Backend API for awesome-crawler web application",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    stats = data_service.get_stats()
    return HealthResponse(
        status="healthy",
        data_loaded=data_service.is_data_loaded(),
        total_items=stats["total_items"],
        last_updated=stats["last_updated"]
    )


@app.get("/api/v1/timeline", response_model=TimelineResponse)
async def get_timeline(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=50, description="Items per page")
):
    """Get paginated timeline (grouped by days)"""
    if not data_service.is_data_loaded():
        raise HTTPException(status_code=503, detail="Data not loaded")

    timeline, total_pages = data_service.get_timeline_page(page, size)
    total_days = len(data_service.timeline)

    return TimelineResponse(
        timeline=timeline,
        page=page,
        size=size,
        total=total_days,
        total_pages=total_pages
    )


@app.get("/api/v1/items", response_model=ItemsResponse)
async def get_items(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Get paginated items"""
    if not data_service.is_data_loaded():
        raise HTTPException(status_code=503, detail="Data not loaded")

    items, total_pages = data_service.get_items_page(page, size)
    total_items = len(data_service.items)

    return ItemsResponse(
        items=items,
        page=page,
        size=size,
        total=total_items,
        total_pages=total_pages
    )


@app.get("/api/v1/search", response_model=ItemsResponse)
async def search_items(
    q: str = Query(..., description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort: str = Query("date", pattern="^(relevance|date)$", description="Sort by relevance or date")
):
    """Search items with fuzzy matching"""
    if not data_service.is_data_loaded():
        raise HTTPException(status_code=503, detail="Data not loaded")

    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Search query is required")

    items, total_pages = data_service.search_items(q, page, size, sort)
    total_matches = data_service.count_search_results(q)

    return ItemsResponse(
        items=items,
        page=page,
        size=size,
        total=total_matches,
        total_pages=total_pages
    )


@app.get("/api/v1/lucky")
async def feeling_lucky():
    """Get a random list"""
    if not data_service.is_data_loaded():
        raise HTTPException(status_code=503, detail="Data not loaded")

    random_data = data_service.get_random_list()

    # Return in same format as timeline for consistency
    return {
        "timeline": [random_data],
        "page": 1,
        "size": 1,
        "total": 1,
        "total_pages": 1
    }


@app.post("/api/v1/reload")
async def reload_data():
    """Reload data from configured source"""
    source_name = DATA_SOURCE.upper()
    logger.info(f"Reloading data from {source_name}...")

    success = data_service.load_data()
    if not success:
        raise HTTPException(status_code=500, detail=f"Failed to reload data from {source_name}")

    stats = data_service.get_stats()
    return {
        "status": "success",
        "message": f"Data reloaded successfully from {source_name}",
        "data_source": DATA_SOURCE,
        "total_items": stats["total_items"],
        "total_lists": stats["total_lists"],
        "last_updated": stats["last_updated"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
