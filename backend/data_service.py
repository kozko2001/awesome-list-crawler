import json
import logging
from datetime import datetime
from typing import List, Optional
from itertools import groupby

import boto3
from fuzzywuzzy import fuzz, process
from botocore.exceptions import ClientError

from models import JSONData, AppItem, AppDayData

logger = logging.getLogger(__name__)


class DataService:
    def __init__(self, bucket_name: str = "awesome-crawler.allocsoc.net", s3_key: str = "data.json"):
        self.bucket_name = bucket_name
        self.s3_key = s3_key
        self.s3_client = boto3.client("s3")
        self.raw_data: Optional[JSONData] = None
        self.items: List[AppItem] = []
        self.timeline: List[AppDayData] = []
        self.last_updated: Optional[datetime] = None
        
    def load_data_from_s3(self) -> bool:
        """Load data from S3 and process it into memory structures"""
        try:
            logger.info(f"Loading data from S3: s3://{self.bucket_name}/{self.s3_key}")
            
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=self.s3_key)
            content = response['Body'].read().decode('utf-8')
            
            data_dict = json.loads(content)
            self.raw_data = JSONData(**data_dict)
            
            # Convert to internal format
            self._process_data()
            self.last_updated = datetime.now()
            
            logger.info(f"Successfully loaded {len(self.items)} items from {len(self.raw_data.lists)} lists")
            return True
            
        except ClientError as e:
            logger.error(f"Error loading from S3: {e}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error loading data: {e}")
            return False
    
    def _process_data(self):
        """Convert raw JSON data to internal AppItem format"""
        if not self.raw_data:
            return
            
        items = []
        for list_data in self.raw_data.lists:
            for item in list_data.items:
                try:
                    # Parse the time string - handle different formats
                    time_str = item.time.split("T")[0]  # Get date part only
                    time_obj = datetime.fromisoformat(time_str)
                    
                    app_item = AppItem(
                        name=item.name,
                        description=item.description,
                        source=item.source,
                        list_name=list_data.name,
                        list_source=list_data.source,
                        time=time_obj
                    )
                    items.append(app_item)
                except Exception as e:
                    logger.warning(f"Error processing item {item.name}: {e}")
                    continue
        
        self.items = items
        self._build_timeline()
    
    def _build_timeline(self):
        """Group items by date and build timeline"""
        if not self.items:
            self.timeline = []
            return
        
        # Sort items by date
        sorted_items = sorted(self.items, key=lambda x: x.time)
        
        # Group by date
        grouped_items = []
        for date, group in groupby(sorted_items, key=lambda x: x.time):
            day_items = list(group)
            day_data = AppDayData(
                items=day_items,
                date=date
            )
            grouped_items.append(day_data)
        
        # Sort timeline by date descending (most recent first)
        self.timeline = sorted(grouped_items, key=lambda x: x.date, reverse=True)
    
    def get_timeline_page(self, page: int = 1, size: int = 10) -> tuple[List[AppDayData], int]:
        """Get paginated timeline (days)"""
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        
        paginated_timeline = self.timeline[start_idx:end_idx]
        total_pages = (len(self.timeline) + size - 1) // size
        
        return paginated_timeline, total_pages
    
    def get_items_page(self, page: int = 1, size: int = 20) -> tuple[List[AppItem], int]:
        """Get paginated items"""
        # Sort items by time descending (most recent first)
        sorted_items = sorted(self.items, key=lambda x: x.time, reverse=True)
        
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        
        paginated_items = sorted_items[start_idx:end_idx]
        total_pages = (len(sorted_items) + size - 1) // size
        
        return paginated_items, total_pages
    
    def search_items(self, query: str, page: int = 1, size: int = 20) -> tuple[List[AppItem], int]:
        """Search items using fuzzy matching"""
        if not query or not query.strip():
            return self.get_items_page(page, size)
        
        query = query.strip().lower()
        
        # Create searchable strings for each item
        searchable_items = []
        for item in self.items:
            # Combine all searchable fields with weights
            searchable_text = f"{item.name} {item.description} {item.list_name} {item.source}".lower()
            searchable_items.append((searchable_text, item))
        
        # Use fuzzywuzzy to find matches
        matches = []
        for searchable_text, item in searchable_items:
            # Calculate fuzzy match score
            score = max(
                fuzz.partial_ratio(query, item.name.lower()) * 0.4,
                fuzz.partial_ratio(query, item.description.lower()) * 0.3,
                fuzz.partial_ratio(query, item.list_name.lower()) * 0.2,
                fuzz.partial_ratio(query, item.source.lower()) * 0.1
            )
            
            # Include items with score > 60
            if score > 60:
                matches.append((score, item))
        
        # Sort by score descending, then by time descending
        matches.sort(key=lambda x: (-x[0], -x[1].time.timestamp()))
        filtered_items = [item for score, item in matches]
        
        # Paginate results
        start_idx = (page - 1) * size
        end_idx = start_idx + size
        
        paginated_items = filtered_items[start_idx:end_idx]
        total_pages = (len(filtered_items) + size - 1) // size
        
        return paginated_items, total_pages
    
    def get_random_list(self) -> AppDayData:
        """Get a random list converted to timeline format"""
        if not self.raw_data or not self.raw_data.lists:
            return AppDayData(items=[], date=datetime.now())
        
        import random
        random_list = random.choice(self.raw_data.lists)
        
        # Convert list items to AppItems
        items = []
        for item in random_list.items:
            try:
                time_str = item.time.split("T")[0]
                time_obj = datetime.fromisoformat(time_str)
                
                app_item = AppItem(
                    name=item.name,
                    description=item.description,
                    source=item.source,
                    list_name=random_list.name,
                    list_source=random_list.source,
                    time=time_obj
                )
                items.append(app_item)
            except Exception as e:
                logger.warning(f"Error processing random item {item.name}: {e}")
                continue
        
        # Sort by time descending
        items.sort(key=lambda x: x.time, reverse=True)
        
        return AppDayData(
            items=items,
            date=items[0].time if items else datetime.now()
        )
    
    def is_data_loaded(self) -> bool:
        """Check if data is loaded"""
        return self.raw_data is not None and len(self.items) > 0
    
    def get_stats(self) -> dict:
        """Get data statistics"""
        return {
            "total_lists": len(self.raw_data.lists) if self.raw_data else 0,
            "total_items": len(self.items),
            "last_updated": self.last_updated
        }