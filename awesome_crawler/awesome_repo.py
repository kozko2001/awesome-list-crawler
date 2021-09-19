import io
import logging
import shutil
import time
from dataclasses import dataclass
from itertools import groupby
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable

import git

from awesome_crawler.extractor import ExtractInfo, extract

logger = logging.getLogger(__name__)


@dataclass
class AwesomeItemTime:
    item: ExtractInfo
    time: time.struct_time


def clone(url: str, dest: Path):
    if dest.exists():
        shutil.rmtree(dest)

    return git.Repo.clone_from(url, dest)


def extract_all_commits(url: str, dest: Path, limit=None):
    repo = clone(url, dest)
    commits = list(repo.iter_commits(max_count=limit))

    for commit in commits:
        readme_filename = find_readme_file(commit)

        if readme_filename:
            targetfile = commit.tree / readme_filename
            with io.BytesIO(targetfile.data_stream.read()) as f:
                markdown = f.read().decode("utf-8")
                items = extract(markdown)

                for item in items:
                    yield AwesomeItemTime(item, time.gmtime(commit.committed_date))


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


def process_awesome_repo(url: str, limit: int = None):
    with TemporaryDirectory() as temp:
        dest = Path(temp)
        x = list(extract_all_commits(url, dest, limit))
        return get_first_date(x)
