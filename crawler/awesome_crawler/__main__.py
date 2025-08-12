import logging
from pathlib import Path

import click

from awesome_crawler.find_awesome_repos import find_repos
from awesome_crawler.output import generate_json
from awesome_crawler.process import crawl_awesome


@click.command()
@click.option("--all/--no-all", default=False)
@click.option("--logs/--no-logs", default=False)
@click.option("--write-s3/--no-write-s3", default=True)
def main(all: bool, logs: bool, write_s3: bool):
    print(f"logs: {logs} all: {all} write_s3: {write_s3}")
    if logs:
        logging.basicConfig(filename="crawler.log", level=logging.INFO)
    else:
        logging.basicConfig(level=logging.ERROR)

    list_of_awesome_projects = find_repos()
    limit_commits = None if all else 10
    items = crawl_awesome(list_of_awesome_projects, limit_commits)
    items_flatten = [x for i in items for x in i]

    dest = None if write_s3 else Path("./output.json")
    generate_json(items_flatten, dest)


if __name__ == "__main__":
    main()
