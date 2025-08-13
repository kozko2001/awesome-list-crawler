from itertools import groupby
from pathlib import Path
import logging

import boto3
import requests

from awesome_crawler.delta import delta
from awesome_crawler.process import AwesomeItem, AwesomeList
from awesome_crawler.serialize import Output, OutputItem, OutputList, serialize

logger = logging.getLogger(__name__)


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


def notify_backend_reload():
    """Notify the backend API to reload data from S3"""
    backend_url = "https://awesome.allocsoc.net/api/v1/reload"
    
    try:
        logger.info(f"Notifying backend to reload data: {backend_url}")
        response = requests.post(backend_url, timeout=30)
        
        if response.status_code == 200:
            logger.info("Backend reload notification sent successfully")
            logger.debug(f"Backend response: {response.text}")
        else:
            logger.warning(f"Backend reload notification failed with status {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to notify backend reload: {e}")
    except Exception as e:
        logger.error(f"Unexpected error notifying backend reload: {e}")


def generate_json(awesomeItems: list[AwesomeItem], dest: Path = None):
    content = generate_json_str(awesomeItems)

    added_new = delta(content)
    content = serialize(added_new)

    if not dest:
        write_to_s3(content)
        # Notify backend to reload data after S3 upload
        notify_backend_reload()
    else:
        write_to_file(content, dest)
