import dataclasses
import json
from itertools import groupby
from pathlib import Path

import boto3

from awesome_crawler.process import AwesomeItem, AwesomeList


@dataclasses.dataclass
class OutputItem:
    name: str
    source: str
    description: str
    time: str


@dataclasses.dataclass
class OutputList:
    name: str
    source: str
    description: str
    items: list[OutputItem]


@dataclasses.dataclass
class Output:
    lists: list[OutputList]


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


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
    return json.dumps(Output(lists), cls=EnhancedJSONEncoder)


def generate_json(awesomeItems: list[AwesomeItem], dest: Path):
    content = generate_json_str(awesomeItems)
    client = boto3.client("s3")
    client.put_object(
        Body=content, Bucket="awesome-crawler.allocsoc.net", Key="data.json"
    )
