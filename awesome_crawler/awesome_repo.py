import io
import shutil
import time
from dataclasses import dataclass
from itertools import groupby
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable

import git
from git.repo.base import Repo

from awesome_crawler.extractor import ExtractInfo, extract


@dataclass
class AwesomeItemTime:
    item: ExtractInfo
    time: time.struct_time


def clone(url: str, dest: Path):
    if dest.exists():
        shutil.rmtree(dest)

    return git.Repo.clone_from(url, dest)


def extract_all_commits(repo: Repo):

    commits = list(repo.iter_commits("master"))

    for commit in commits:
        targetfile = commit.tree / "README.md"
        with io.BytesIO(targetfile.data_stream.read()) as f:
            markdown = f.read().decode("utf-8")
            items = extract(markdown)

            for item in items:
                yield AwesomeItemTime(item, time.gmtime(commit.committed_date))


def get_first_date(items: list[AwesomeItemTime]) -> Iterable[AwesomeItemTime]:
    items.sort(key=lambda i: i.item.name)

    for key, group in groupby(items, lambda x: x.item.name):

        g = list(group)
        g.sort(key=lambda i: i.time)

        yield AwesomeItemTime(g[-1].item, g[0].time)


def process_awesome_repo(url: str):
    with TemporaryDirectory() as temp:
        dest = Path(temp)
        repo = clone(url, dest)
        x = list(extract_all_commits(repo))
        return get_first_date(x)
