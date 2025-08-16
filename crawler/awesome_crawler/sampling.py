import random
import logging
from datetime import datetime, timedelta
from typing import List

from awesome_crawler.process import AwesomeList
from awesome_crawler.serialize import Output, OutputList

logger = logging.getLogger(__name__)


def get_last_update_time(repo_data: OutputList) -> datetime:
    """Get the most recent update time from a repository's items"""
    if not repo_data.items:
        return datetime.min
    
    latest_time = datetime.min
    for item in repo_data.items:
        try:
            item_time = datetime.fromisoformat(item.time)
            if item_time > latest_time:
                latest_time = item_time
        except ValueError:
            continue
    
    return latest_time


def calculate_sampling_probability(last_update: datetime) -> float:
    """Calculate sampling probability based on last update time
    
    Rules:
    - Last month: 90% probability
    - Last 1 year: 50% probability  
    - Last 2 years: 20% probability
    - More than 3 years: 5% probability
    """
    now = datetime.now()
    time_diff = now - last_update
    
    if time_diff <= timedelta(days=30):  # Last month
        return 0.9
    elif time_diff <= timedelta(days=365):  # Last year
        return 0.5
    elif time_diff <= timedelta(days=730):  # Last 2 years
        return 0.2
    elif time_diff <= timedelta(days=1095):  # Last 3 years
        return 0.05
    else:  # More than 3 years
        return 0.05


def filter_repositories_by_activity(repos: List[AwesomeList], s3_data: Output) -> List[AwesomeList]:
    """Filter repositories based on their last update activity using probabilistic sampling"""
    if not s3_data or not s3_data.lists:
        logger.info("No S3 data available, processing all repositories")
        return repos
    
    # Create lookup for S3 data by repository name
    s3_lookup = {repo_data.name: repo_data for repo_data in s3_data.lists}
    
    filtered_repos = []
    total_repos = len(repos)
    
    for repo in repos:
        repo_data = s3_lookup.get(repo.name)
        
        if not repo_data:
            # New repository not in S3 data - always include
            filtered_repos.append(repo)
            logger.debug(f"Including new repository: {repo.name}")
            continue
        
        last_update = get_last_update_time(repo_data)
        probability = calculate_sampling_probability(last_update)
        
        # Random sampling based on probability
        if random.random() < probability:
            filtered_repos.append(repo)
            logger.debug(f"Including repository: {repo.name} (last update: {last_update.strftime('%Y-%m-%d')}, probability: {probability:.0%})")
        else:
            logger.debug(f"Skipping repository: {repo.name} (last update: {last_update.strftime('%Y-%m-%d')}, probability: {probability:.0%})")
    
    filtered_count = len(filtered_repos)
    logger.info(f"Probabilistic sampling: {filtered_count}/{total_repos} repositories selected ({filtered_count/total_repos:.1%})")
    
    return filtered_repos


def log_sampling_statistics(repos: List[AwesomeList], s3_data: Output):
    """Log statistics about repository update times for analysis"""
    if not s3_data or not s3_data.lists:
        return
    
    s3_lookup = {repo_data.name: repo_data for repo_data in s3_data.lists}
    stats = {
        "last_month": 0,
        "last_year": 0, 
        "last_2_years": 0,
        "older_than_3_years": 0,
        "no_data": 0
    }
    
    for repo in repos:
        repo_data = s3_lookup.get(repo.name)
        if not repo_data:
            stats["no_data"] += 1
            continue
            
        last_update = get_last_update_time(repo_data)
        now = datetime.now()
        time_diff = now - last_update
        
        if time_diff <= timedelta(days=30):
            stats["last_month"] += 1
        elif time_diff <= timedelta(days=365):
            stats["last_year"] += 1
        elif time_diff <= timedelta(days=730):
            stats["last_2_years"] += 1
        else:
            stats["older_than_3_years"] += 1
    
    total = len(repos)
    logger.info(f"Repository activity distribution:")
    logger.info(f"  Last month: {stats['last_month']}/{total} ({stats['last_month']/total:.1%}) - 90% sampling rate")
    logger.info(f"  Last year: {stats['last_year']}/{total} ({stats['last_year']/total:.1%}) - 50% sampling rate") 
    logger.info(f"  Last 2 years: {stats['last_2_years']}/{total} ({stats['last_2_years']/total:.1%}) - 20% sampling rate")
    logger.info(f"  Older than 3 years: {stats['older_than_3_years']}/{total} ({stats['older_than_3_years']/total:.1%}) - 5% sampling rate")
    logger.info(f"  No data: {stats['no_data']}/{total} ({stats['no_data']/total:.1%}) - 100% sampling rate")