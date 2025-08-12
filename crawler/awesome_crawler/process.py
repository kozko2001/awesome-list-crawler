import logging
from dataclasses import dataclass
from datetime import datetime
from multiprocessing import Pool
from typing import Optional

import tqdm

from awesome_crawler.awesome_repo import process_awesome_repo
from awesome_crawler.extractor import ExtractInfo

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


def crawl_repository(argument: CrawlerArgument):
    awesomeList = argument.list
    try:
        items = process_awesome_repo(
            awesomeList.source.split("#")[0], limit=argument.limit
        )
        logger.error(f"succesful processed repo {awesomeList}")
        return [AwesomeItem(item.item, awesomeList, item.time) for item in items]
    except Exception:
        logger.exception(f"failed to process repo {awesomeList}")
        return []


def crawl_awesome(awesomeLists: list[AwesomeList], limit: Optional[int] = None):
    arguments = [CrawlerArgument(list, limit) for list in awesomeLists]
    with Pool(8) as p:
        return list(
            tqdm.tqdm(p.imap(crawl_repository, arguments), total=len(awesomeLists))
        )
