import io
import shutil
import time
from pathlib import Path

import git
from git.repo.base import Repo

from awesome_crawler.extractor import extract


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
            yield (extract(markdown), time.gmtime(commit.committed_date))
