import logging
import os
import signal
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


class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError("Repository processing timed out")

def crawl_repository(argument: CrawlerArgument):
    awesomeList = argument.list
    
    logger.debug(f"🚀 Starting to process repository: {awesomeList.name}")
    logger.debug(f"📍 Repository URL: {awesomeList.source}")
    logger.debug(f"📝 Repository description: {awesomeList.description}")
    logger.debug(f"⏰ Processing since date: {argument.since_date}")
    logger.debug(f"🔢 Item limit: {argument.limit}")
    
    # Set up timeout (240 seconds = 4 minutes)
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(240)
    
    try:
        repo_url = awesomeList.source.split("#")[0]
        logger.debug(f"🔗 Cleaned repository URL: {repo_url}")
        
        items = process_awesome_repo(
            repo_url, 
            limit=argument.limit,
            since_date=argument.since_date
        )
        
        signal.alarm(0)  # Cancel the alarm
        items_list = [AwesomeItem(item.item, awesomeList, item.time) for item in items]
        
        logger.info(f"✅ Successfully processed repo {awesomeList.name} - found {len(items_list)} items")
        logger.debug(f"📊 Items found: {[item.item.name for item in items_list[:10]]}{'...' if len(items_list) > 10 else ''}")
        
        return items_list
    except TimeoutError:
        signal.alarm(0)  # Cancel the alarm
        logger.error(f"⏱️ Repository {awesomeList.name} timed out after 4 minutes, skipping")
        return []
    except Exception as e:
        signal.alarm(0)  # Cancel the alarm
        logger.exception(f"❌ Failed to process repo {awesomeList.name}: {str(e)}")
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
            tqdm.tqdm(p.imap_unordered(crawl_repository, arguments), total=len(awesomeLists))
        )
