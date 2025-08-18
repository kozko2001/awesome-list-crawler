import logging
import os
from dataclasses import dataclass
from datetime import datetime
from multiprocessing import Pool
from typing import Optional

import tqdm

from awesome_crawler.awesome_repo import process_awesome_repo
from awesome_crawler.extractor import ExtractInfo
from awesome_crawler.serialize import Output

logger = logging.getLogger(__name__)


@dataclass
class AwesomeList:
    name: str
    source: str
    description: str


@dataclass
class AwesomeItem:
    item: ExtractInfo
    list: AwesomeList
    time: datetime


@dataclass
class CrawlerArgument:
    list: AwesomeList
    limit: Optional[int]
    since_date: Optional[datetime] = None


def crawl_repository(argument: CrawlerArgument):
    awesomeList = argument.list
    try:
        items = process_awesome_repo(
            awesomeList.source.split("#")[0], 
            limit=argument.limit,
            since_date=argument.since_date
        )
        logger.info(f"successfully processed repo {awesomeList}")
        return [AwesomeItem(item.item, awesomeList, item.time) for item in items]
    except Exception:
        logger.exception(f"failed to process repo {awesomeList}")
        return []


def get_latest_timestamp_for_repo(repo_source: str, s3_data: Optional[Output]) -> Optional[datetime]:
    """Get the latest timestamp for items in a repository from S3 data"""
    if not s3_data:
        logger.info(f"No S3 data available for {repo_source}, will process all commits")
        return None
    
    # Normalize URL for comparison - remove fragments and trailing slashes
    def normalize_url(url):
        return url.strip().split("#")[0].rstrip("/")
    
    normalized_source = normalize_url(repo_source)
    logger.debug(f"Looking for timestamp for normalized URL: {normalized_source}")
    
    for list_data in s3_data.lists:
        normalized_list_source = normalize_url(list_data.source)
        if normalized_list_source == normalized_source:
            logger.info(f"✅ Found matching repository in data: {list_data.source} -> {repo_source}")
            
            if list_data.items:
                # Find the latest timestamp among all items in this list
                latest_time = None
                for item in list_data.items:
                    try:
                        item_time = datetime.fromisoformat(item.time.replace('Z', '+00:00'))
                        if latest_time is None or item_time > latest_time:
                            latest_time = item_time
                    except (ValueError, AttributeError):
                        continue
                
                if latest_time:
                    logger.info(f"📅 Found latest timestamp {latest_time} for repo {repo_source} (from {len(list_data.items)} items)")
                    return latest_time
                else:
                    logger.warning(f"Repository {repo_source} found but no valid timestamps in items")
            else:
                logger.warning(f"Repository {repo_source} found but has no items")
            
            return None
    
    logger.info(f"❌ Repository {repo_source} not found in data, will process all commits")
    return None


def crawl_awesome(awesomeLists: list[AwesomeList], limit: Optional[int] = None, s3_data: Optional[Output] = None):
    # Create arguments with incremental processing info
    arguments = []
    for awesome_list in awesomeLists:
        since_date = get_latest_timestamp_for_repo(awesome_list.source, s3_data)
        arguments.append(CrawlerArgument(awesome_list, limit, since_date))
    
    # Dynamic CPU count based on available resources
    cpu_count = min(os.cpu_count() or 4, len(awesomeLists), 4)
    logger.info(f"Using {cpu_count} processes for crawling {len(awesomeLists)} repositories")
    
    with Pool(cpu_count) as p:
        return list(
            tqdm.tqdm(p.imap(crawl_repository, arguments), total=len(awesomeLists))
        )
