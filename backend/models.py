from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class JSONItem(BaseModel):
    name: str
    source: str
    description: str
    time: str


class JSONList(BaseModel):
    name: str
    description: str
    source: str
    items: List[JSONItem]


class JSONData(BaseModel):
    lists: List[JSONList]


class AppItem(BaseModel):
    name: str
    description: str
    source: str
    list_name: str
    list_source: str
    time: datetime


class AppDayData(BaseModel):
    items: List[AppItem]
    date: datetime


class PaginatedResponse(BaseModel):
    data: List[dict]
    page: int
    size: int
    total: int
    total_pages: int


class TimelineResponse(BaseModel):
    timeline: List[AppDayData]
    page: int
    size: int
    total: int
    total_pages: int


class ItemsResponse(BaseModel):
    items: List[AppItem]
    page: int
    size: int
    total: int
    total_pages: int


class HealthResponse(BaseModel):
    status: str
    data_loaded: bool
    total_items: int
    last_updated: Optional[datetime] = None