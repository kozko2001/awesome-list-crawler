from typing import Optional

import boto3

from awesome_crawler.serialize import Output, deserialize


def get_last() -> str:
    client = boto3.client("s3")
    obj = client.get_object(Bucket="awesome-crawler.allocsoc.net", Key="data.json")
    return obj["Body"].read()


def find_list(list, name):
    p = [x for x in list if x.name == name]
    return p[0] if p else None


def delta(new_data: str, old_data: Optional[str] = None) -> Output:
    new: Output = deserialize(new_data)
    old: Output = deserialize(old_data if old_data else get_last())

    lists = []

    for old_list in old.lists:
        new_list = find_list(new.lists, old_list.name)
        f = []
        to_append = []
        if new_list:

            for old_item in old_list.items:
                new_item = find_list(new_list.items, old_item.name)

                if new_item:
                    f.append(new_item.name)

            to_append = [item for item in new_list.items if item.name not in f]
        print(f"for list {old_list.name} to_append is {to_append}")
        old_list.items = old_list.items + to_append
        lists.append(old_list)

    return Output(lists)
