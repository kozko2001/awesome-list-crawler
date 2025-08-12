from itertools import groupby
from pathlib import Path

import boto3

from awesome_crawler.delta import delta
from awesome_crawler.process import AwesomeItem, AwesomeList
from awesome_crawler.serialize import Output, OutputItem, OutputList, serialize


def generate_json_str(awesomeItems: list[AwesomeItem]) -> str:
    awesomeItems.sort(key=lambda item: item.list.name)

    lists = []

    for key, _group in groupby(awesomeItems, lambda x: x.list.name):
        group = list(_group)
        l: AwesomeList = group[0].list

        group.sort(key=lambda i: i.item.name)

        items = [
            OutputItem(
                i.item.name, i.item.source, i.item.description, i.time.isoformat()
            )
            for i in group
        ]
        lists.append(OutputList(l.name, l.source, l.description, items))
    return serialize(Output(lists))


def write_to_s3(content: str):
    client = boto3.client("s3")
    client.put_object(
        Body=content, Bucket="awesome-crawler.allocsoc.net", Key="data.json"
    )


def write_to_file(content: str, dest: Path):
    with dest.open("w") as f:
        f.write(content)


def generate_json(awesomeItems: list[AwesomeItem], dest: Path = None):
    content = generate_json_str(awesomeItems)

    added_new = delta(content)
    content = serialize(added_new)

    if not dest:
        write_to_s3(content)
    else:
        write_to_file(content, dest)
