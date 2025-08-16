import json
import logging
import os
import tempfile
from datetime import datetime
from typing import List, Optional
from itertools import groupby

import boto3
import tantivy
from botocore.exceptions import ClientError

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from models import JSONData, AppItem, AppDayData

logger = logging.getLogger(__name__)


class DataService:
    def __init__(self, 
                 data_source: str = "s3",
                 bucket_name: str = "awesome-crawler.allocsoc.net", 
                 s3_key: str = "data.json",
                 local_file_path: str = "data/data.json"):
        self.data_source = data_source.lower()
        self.bucket_name = bucket_name
        self.s3_key = s3_key
        self.local_file_path = local_file_path
        
        # Only initialize S3 client if using S3
        if self.data_source == "s3":
            self.s3_client = boto3.client("s3")
        else:
            self.s3_client = None
            
        self.raw_data: Optional[JSONData] = None
        self.items: List[AppItem] = []
        self.timeline: List[AppDayData] = []
        self.last_updated: Optional[datetime] = None
        # Tantivy search index
        self.search_index: Optional[tantivy.Index] = None
        self.searcher: Optional[tantivy.Searcher] = None
        
    def load_data(self) -> bool:
        """Load data from configured source (S3 or local file)"""
        if self.data_source == "s3":
            return self._load_data_from_s3()
        elif self.data_source == "local":
            return self._load_data_from_local()
        else:
            logger.error(f"Unknown data source: {self.data_source}")
            return False
    
    def _load_data_from_s3(self) -> bool:
        """Load data from S3 and process it into memory structures"""
        try:
            logger.info(f"Loading data from S3: s3://{self.bucket_name}/{self.s3_key}")
            
            if not self.s3_client:
                logger.error("S3 client not initialized")
                return False
            
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=self.s3_key)
            content = response['Body'].read().decode('utf-8')
            
            data_dict = json.loads(content)
            self.raw_data = JSONData(**data_dict)
            logger.info(f"Data from S3 successfully loaded into memory - {len(data_dict.get('lists', []))} lists parsed")
            
            # Convert to internal format
            self._process_data()
            self.last_updated = datetime.now()
            
            logger.info(f"Successfully loaded {len(self.items)} items from {len(self.raw_data.lists)} lists")
            return True
            
        except Exception as e:
            logger.error(f"Error loading from S3: {e}")
            return False
    
    def _load_data_from_local(self) -> bool:
        """Load data from local file and process it into memory structures"""
        try:
            logger.info(f"Loading data from local file: {self.local_file_path}")
            
            if not os.path.exists(self.local_file_path):
                logger.error(f"Local file not found: {self.local_file_path}")
                return False
            
            with open(self.local_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            data_dict = json.loads(content)
            self.raw_data = JSONData(**data_dict)
            logger.info(f"Data from local file successfully loaded into memory - {len(data_dict.get('lists', []))} lists parsed")
            
            # Convert to internal format
            self._process_data()
            self.last_updated = datetime.now()
            
            logger.info(f"Successfully loaded {len(self.items)} items from {len(self.raw_data.lists)} lists")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from local file: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error loading local data: {e}")
            return False

    # Keep backward compatibility
    def load_data_from_s3(self) -> bool:
        """Backward compatibility method - use load_data() instead"""
        return self._load_data_from_s3()
    
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
        self._build_search_index()
    
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
    
    def _build_search_index(self):
        """Build Tantivy search index for fast full-text search"""
        if not self.items:
            return
        
        logger.info(f"Starting to build search index for {len(self.items)} items...")
        
        try:
            # Create schema with fields for searching
            schema_builder = tantivy.SchemaBuilder()
            schema_builder.add_text_field("name", stored=True)
            schema_builder.add_text_field("description", stored=True)
            schema_builder.add_text_field("list_name", stored=True)
            schema_builder.add_text_field("source", stored=True)
            schema_builder.add_integer_field("item_id", stored=True, indexed=True)
            schema = schema_builder.build()
            
            # Create index in memory
            self.search_index = tantivy.Index(schema, path=None)
            
            # Index all items
            writer = self.search_index.writer()
            for i, item in enumerate(self.items):
                writer.add_document(tantivy.Document(
                    name=item.name or "",
                    description=item.description or "",
                    list_name=item.list_name or "",
                    source=item.source or "",
                    item_id=i
                ))
            writer.commit()
            
            # Create searcher
            self.search_index.reload()
            self.searcher = self.search_index.searcher()
            
            logger.info(f"Search index build completed successfully - indexed {len(self.items)} items")
            
            # Log memory usage after index building
            if PSUTIL_AVAILABLE:
                process = psutil.Process()
                memory_info = process.memory_info()
                logger.info(f"Memory usage after index build: RSS={memory_info.rss / 1024 / 1024:.1f}MB, VMS={memory_info.vms / 1024 / 1024:.1f}MB")
            
        except Exception as e:
            logger.error(f"Error building search index: {e}")
            self.search_index = None
            self.searcher = None
    
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
    
    def search_items(self, query: str, page: int = 1, size: int = 20, sort: str = "date") -> tuple[List[AppItem], int]:
        """Search items using Tantivy full-text search"""
        if not query or not query.strip():
            return self.get_items_page(page, size)
        
        if not self.searcher or not self.search_index:
            logger.warning("Search index not available, falling back to pagination")
            return self.get_items_page(page, size)
        
        try:
            query = query.strip()
            
            # Parse the query - search across all fields
            parsed_query = self.search_index.parse_query(query, ["name", "description", "list_name", "source"])
            
            # Search with a reasonable limit (we'll paginate after)
            max_results = max(1000, (page * size))
            top_docs = self.searcher.search(parsed_query, max_results)
            
            # Extract items using the stored item_id
            matched_items = []
            for score, doc_address in top_docs.hits:
                doc = self.searcher.doc(doc_address)
                item_id = doc["item_id"][0]
                if 0 <= item_id < len(self.items):
                    if sort == "relevance":
                        # Store score with item for relevance sorting
                        item = self.items[item_id]
                        item._search_score = score  # Add temporary score attribute
                        matched_items.append(item)
                    else:
                        matched_items.append(self.items[item_id])
            
            # Sort results based on sort parameter
            if sort == "relevance":
                # Sort by search score (highest first) - already in relevance order from Tantivy
                matched_items.sort(key=lambda x: getattr(x, '_search_score', 0), reverse=True)
            else:  # sort == "date"
                # Sort by date (most recent first)
                matched_items.sort(key=lambda x: x.time, reverse=True)
            
            # Clean up temporary score attributes
            if sort == "relevance":
                for item in matched_items:
                    if hasattr(item, '_search_score'):
                        delattr(item, '_search_score')
            
            # Paginate results
            total_matches = len(matched_items)
            start_idx = (page - 1) * size
            end_idx = start_idx + size
            
            paginated_items = matched_items[start_idx:end_idx]
            total_pages = (total_matches + size - 1) // size
            
            return paginated_items, total_pages
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            # Fallback to regular pagination
            return self.get_items_page(page, size)
    
    def count_search_results(self, query: str) -> int:
        """Count total search results without pagination"""
        if not query or not query.strip():
            return len(self.items)
        
        if not self.searcher or not self.search_index:
            return len(self.items)
        
        try:
            query = query.strip()
            parsed_query = self.search_index.parse_query(query, ["name", "description", "list_name", "source"])
            
            # Search with high limit to get accurate count
            top_docs = self.searcher.search(parsed_query, 10000)
            return len(top_docs.hits)
            
        except Exception as e:
            logger.error(f"Search count error: {e}")
            return len(self.items)
    
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