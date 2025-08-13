import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

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

# Global data service instance
data_service = DataService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting awesome-crawler backend...")
    
    # Load initial data from S3
    success = data_service.load_data_from_s3()
    if not success:
        logger.warning("Failed to load initial data from S3")
    
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
    size: int = Query(20, ge=1, le=100, description="Items per page")
):
    """Search items with fuzzy matching"""
    if not data_service.is_data_loaded():
        raise HTTPException(status_code=503, detail="Data not loaded")
    
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Search query is required")
    
    items, total_pages = data_service.search_items(q, page, size)
    
    # For search, we need to count total matching items (not all items)
    # This is approximate since we're doing pagination after scoring
    all_matches, _ = data_service.search_items(q, 1, 10000)  # Get all matches
    total_matches = len(all_matches)
    
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
    """Reload data from S3"""
    logger.info("Reloading data from S3...")
    
    success = data_service.load_data_from_s3()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to reload data from S3")
    
    stats = data_service.get_stats()
    return {
        "status": "success",
        "message": "Data reloaded successfully",
        "total_items": stats["total_items"],
        "total_lists": stats["total_lists"],
        "last_updated": stats["last_updated"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)