import logging
import time
from pathlib import Path
from typing import List, Set

from github import Github

from awesome_crawler.awesome_repo import process_awesome_repo
from awesome_crawler.process import AwesomeList

logger = logging.getLogger(__name__)


def from_awesome_awesome():
    list_of_awesome_projects = [
        AwesomeList(p.item.name, p.item.source, p.item.description)
        for p in process_awesome_repo("https://github.com/sindresorhus/awesome", 1)
    ]

    return list_of_awesome_projects


def from_github_topics():
    g = Github(per_page=100)

    # Multiple search terms to capture more awesome repositories
    search_terms = [
        "topic:awesome-list",
        "topic:awesome",
        "topic:curated-list", 
        "topic:curated",
        "awesome in:name",
        "awesome-* in:name",
        "curated in:name",
        "list in:name topic:awesome"
    ]
    
    all_repos = {}  # Use dict to deduplicate by full_name
    
    for search_term in search_terms:
        logger.info(f"Searching with term: {search_term}")
        try:
            paginated = g.search_repositories(search_term)
            count = 0
            for repo in paginated:
                # Skip if we already found this repo
                if repo.full_name in all_repos:
                    continue
                    
                # Basic filtering for likely awesome lists
                repo_name_lower = repo.name.lower()
                repo_desc_lower = (repo.description or "").lower()
                
                if (("awesome" in repo_name_lower or "curated" in repo_name_lower or "list" in repo_name_lower) and
                    repo.stargazers_count >= 5):  # Minimum quality filter
                    
                    r = AwesomeList(repo.name, repo.html_url, repo.description)
                    all_repos[repo.full_name] = r
                    print(f"{search_term}: {r} ({repo.stargazers_count} stars)")
                    count += 1
                    
                # Stop after reasonable number per search term to avoid rate limits
                if count >= 200:
                    break
                    
                if count % 100 == 0 and count > 0:
                    time.sleep(6)
                    
        except Exception as e:
            logger.warning(f"Search failed for term '{search_term}': {e}")
            time.sleep(10)  # Longer sleep on error
            continue
        
        # Sleep between search terms to avoid rate limiting
        time.sleep(3)
    
    lists = list(all_repos.values())
    logger.info(f"Found {len(lists)} unique repositories from GitHub topics")
    return lists


def normalize_url(url: str) -> str:
    """Normalize URL for consistent comparison"""
    return url.strip().replace("#readme", "").rstrip("/")


def load_repository_list(file_path: str) -> Set[str]:
    """Load repository URLs from a text file (like .gitignore format)"""
    repos = set()
    path = Path(file_path)
    
    if not path.exists():
        return repos
    
    try:
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    repos.add(normalize_url(line))
        logger.info(f"Loaded {len(repos)} repositories from {file_path}")
    except Exception as e:
        logger.warning(f"Failed to load {file_path}: {e}")
    
    return repos


def load_additional_repositories(file_path: str) -> List[AwesomeList]:
    """Load additional repositories from include file and create AwesomeList objects"""
    additional_repos = []
    repos = load_repository_list(file_path)
    
    for repo_url in repos:
        # Create a basic AwesomeList object for additional repositories
        repo_name = repo_url.split('/')[-1] if '/' in repo_url else repo_url
        additional_repos.append(AwesomeList(repo_name, repo_url, f"Additional repository: {repo_name}"))
    
    return additional_repos


def find_repos():
    awesome_awesome = from_awesome_awesome()
    github_topics = from_github_topics()

    # Remove duplicates between awesome-awesome and github topics
    duplicated_urls = set([normalize_url(r.source) for r in awesome_awesome]) & set([normalize_url(r.source) for r in github_topics])
    github_topics = list(filter(lambda r: normalize_url(r.source) not in duplicated_urls, github_topics))

    # Combine discovered repositories
    repos = awesome_awesome + github_topics
    logger.info(f"Discovered {len(repos)} repositories from standard sources")

    # Load additional repositories from include file
    additional_repos = load_additional_repositories(".crawlerinclude")
    if additional_repos:
        # Remove duplicates between discovered and additional repos
        existing_urls = set([normalize_url(r.source) for r in repos])
        new_additional = [r for r in additional_repos if normalize_url(r.source) not in existing_urls]
        repos.extend(new_additional)
        logger.info(f"Added {len(new_additional)} additional repositories from .crawlerinclude")

    # Load ignore list and filter out ignored repositories
    ignored_repos = load_repository_list(".crawlerignore")
    if ignored_repos:
        original_count = len(repos)
        repos = [r for r in repos if normalize_url(r.source) not in ignored_repos]
        filtered_count = original_count - len(repos)
        if filtered_count > 0:
            logger.info(f"Filtered out {filtered_count} repositories from .crawlerignore")

    logger.info(f"Final repository count: {len(repos)}")
    return repos
