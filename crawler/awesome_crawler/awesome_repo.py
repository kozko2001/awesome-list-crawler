import io
import logging
import shutil
from dataclasses import dataclass
from datetime import datetime
from itertools import groupby
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable, Optional

import git

from awesome_crawler.extractor import ExtractInfo, extract

logger = logging.getLogger(__name__)


@dataclass
class AwesomeItemTime:
    item: ExtractInfo
    time: datetime


def clone(url: str, dest: Path, since_date: Optional[datetime] = None):
    if dest.exists():
        shutil.rmtree(dest)

    env = {"GIT_TERMINAL_PROMPT": "0"}
    
    if since_date:
        # Try shallow clone first, fallback to full clone if it fails
        since_str = since_date.strftime('%Y-%m-%d')
        logger.info(f"Attempting shallow clone of {url} since {since_str}")
        try:
            return git.Repo.clone_from(url, dest, env=env, shallow_since=since_str)
        except git.exc.GitCommandError as e:
            logger.warning(f"Shallow clone failed for {url}, falling back to full clone: {e}")
            # Fallback to full clone if shallow clone fails
            return git.Repo.clone_from(url, dest, env=env)
    else:
        # Full clone for new repositories
        logger.info(f"Full cloning {url}")
        return git.Repo.clone_from(url, dest, env=env)


def extract_all_commits(url: str, dest: Path, limit=None, since_date: Optional[datetime] = None):
    repo = clone(url, dest, since_date)
    
    # If we have a since_date, process commits after that date (already filtered by shallow clone)
    if since_date:
        commits = list(repo.iter_commits(since=since_date))
        logger.info(f"Processing {len(commits)} commits since {since_date} for {url}")
    else:
        # No since_date means new repo - process ALL commits to get complete history
        commits = list(repo.iter_commits())
        logger.info(f"Processing {len(commits)} commits (new repo, all history) for {url}")

    for commit in commits:
        readme_filename = find_readme_file(commit)

        if readme_filename:
            try:
                targetfile = commit.tree / readme_filename
                with io.BytesIO(targetfile.data_stream.read()) as f:
                    markdown = f.read().decode("utf-8", errors='ignore')
                    items = extract(markdown)

                    commit_date = datetime.fromtimestamp(commit.committed_date)
                    for item in items:
                        yield AwesomeItemTime(item, commit_date)
            except Exception as e:
                logger.warning(f"Failed to process commit {commit.hexsha[:8]} in {url}: {e}")
                continue


def find_readme_file(commit):
    filenames = [p.path for p in commit.tree.traverse()]

    readmes = [f for f in filenames if "readme" in f.lower()]
    if readmes:
        return readmes[0]
    else:
        return None


def get_first_date(items: list[AwesomeItemTime]) -> Iterable[AwesomeItemTime]:
    items.sort(key=lambda i: i.item.name)

    for key, group in groupby(items, lambda x: x.item.name):

        g = list(group)
        g.sort(key=lambda i: i.time)

        yield AwesomeItemTime(g[-1].item, g[0].time)


def process_awesome_repo(url: str, limit: int = None, since_date: Optional[datetime] = None) -> Iterable[AwesomeItemTime]:
    logger.debug(f"🔄 Starting processing of repository: {url}")
    logger.debug(f"📁 Creating temporary directory for cloning...")
    
    with TemporaryDirectory() as temp:
        dest = Path(temp)
        logger.debug(f"📂 Temporary directory created: {temp}")
        
        logger.debug(f"🔍 Extracting commits from repository...")
        x = list(extract_all_commits(url, dest, limit, since_date))
        logger.debug(f"📈 Total items extracted from all commits: {len(x)}")
        
        logger.debug(f"🎯 Getting first occurrence dates for items...")
        result = list(get_first_date(x))
        logger.debug(f"✨ Final unique items after deduplication: {len(result)}")
        
        return result
