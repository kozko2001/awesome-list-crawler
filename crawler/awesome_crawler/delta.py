from typing import Optional
import logging

import boto3

from awesome_crawler.serialize import Output, deserialize

logger = logging.getLogger(__name__)


def get_last() -> str:
    logger.info("Fetching last data from S3")
    try:
        client = boto3.client("s3")
        logger.debug("Created S3 client successfully")
        
        obj = client.get_object(Bucket="awesome-crawler.allocsoc.net", Key="data.json")
        data = obj["Body"].read()
        logger.info(f"Successfully fetched {len(data)} bytes from S3")
        return data
    except Exception as e:
        logger.error(f"Failed to fetch last data from S3: {e}")
        raise


def find_list(list, name):
    p = [x for x in list if x.name == name]
    return p[0] if p else None


def delta(new_data: str, old_data: Optional[str] = None) -> Output:
    logger.info("Starting delta calculation")
    
    try:
        logger.debug("Deserializing new data")
        new: Output = deserialize(new_data)
        logger.info(f"New data contains {len(new.lists)} lists")
        
        if old_data:
            logger.debug("Using provided old data")
            old: Output = deserialize(old_data)
        else:
            logger.debug("Fetching old data from S3")
            old: Output = deserialize(get_last())
        
        logger.info(f"Old data contains {len(old.lists)} lists")
        
        lists = []
        total_items_added = 0

        logger.debug("Processing existing lists for delta changes")
        for old_list in old.lists:
            new_list = find_list(new.lists, old_list.name)
            f = []
            to_append = []
            
            if new_list:
                logger.debug(f"Processing list '{old_list.name}' - old: {len(old_list.items)} items, new: {len(new_list.items)} items")
                
                for old_item in old_list.items:
                    new_item = find_list(new_list.items, old_item.name)

                    if new_item:
                        f.append(new_item.name)

                to_append = [item for item in new_list.items if item.name not in f]
                
                if to_append:
                    logger.info(f"List '{old_list.name}': adding {len(to_append)} new items")
                    for item in to_append:
                        logger.debug(f"  - Adding item: {item.name}")
                    total_items_added += len(to_append)
                else:
                    logger.debug(f"List '{old_list.name}': no new items to add")
            else:
                logger.debug(f"List '{old_list.name}' not found in new data")
            
            old_list.items = old_list.items + to_append
            lists.append(old_list)

        logger.debug("Processing completely new lists")
        new_lists_added = 0
        for new_list in new.lists:
            old_list = find_list(lists, new_list.name)

            if not old_list:
                logger.info(f"Adding new list '{new_list.name}' with {len(new_list.items)} items")
                lists.append(new_list)
                new_lists_added += 1
                total_items_added += len(new_list.items)

        logger.info(f"Delta calculation complete: {new_lists_added} new lists, {total_items_added} total new items added")
        return Output(lists)
        
    except Exception as e:
        logger.error(f"Error during delta calculation: {e}")
        raise
