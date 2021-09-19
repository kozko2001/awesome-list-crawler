import logging
from dataclasses import dataclass
from multiprocessing import Pool

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


def crawl_repository(awesomeList: AwesomeList):
    try:
        items = process_awesome_repo(awesomeList.source.split("#")[0], limit=1)
        logger.info(f"succesful processed repo {awesomeList}")
        return [AwesomeItem(item, awesomeList) for item in items]
    except Exception:
        logger.exception(f"failed to process repo {awesomeList}")
        return []


def crawl_awesome(awesomeLists: list[AwesomeList]):
    with Pool(8) as p:
        return list(
            tqdm.tqdm(p.imap(crawl_repository, awesomeLists), total=len(awesomeLists))
        )
