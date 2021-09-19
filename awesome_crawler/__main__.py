import logging
from pathlib import Path

from awesome_crawler.awesome_repo import process_awesome_repo
from awesome_crawler.output import generate_json
from awesome_crawler.process import AwesomeList, crawl_awesome

if __name__ == "__main__":
    logging.basicConfig(filename="crawler.log", level=logging.INFO)

    list_of_awesome_projects = [
        AwesomeList(p.item.name, p.item.source, p.item.description)
        for p in process_awesome_repo("https://github.com/sindresorhus/awesome", 1)
    ]

    items = crawl_awesome(list_of_awesome_projects)
    items_flatten = [x for i in items for x in i]

    generate_json(items_flatten, Path("./output.json"))
