import logging
from dataclasses import dataclass
from typing import Mapping, Optional

import mistune

logger = logging.getLogger(__name__)


@dataclass
class ExtractInfo:
    name: str
    source: str
    description: str
    category: Optional[str]


def extract(source: str) -> list[ExtractInfo]:
    markdown = mistune.create_markdown(renderer="ast")
    ast: Mapping[str, str] = markdown(source)

    list_items = find_list_items(ast)
    items_info = map(map_list_item, list_items)
    return list(filter(None, items_info))


def find_list_items(ast):
    def is_listitem(token):
        return "type" in token and token["type"] == "list_item"

    return filter(is_listitem, flat(ast))


def map_list_item(list_item) -> Optional[ExtractInfo]:
    list_item = [list_item]
    block_text = find_type_single(list_item, "block_text")
    if block_text is None:
        block_text = list_item[0]

    if "children" not in block_text:
        return None

    link_token = find_type_single(get_children(block_text), "link")
    if link_token is None:
        logger.warn(f"no link found... ignoring this item {list_item}")
        return None

    name = get_text([link_token])
    link: str = link_token["link"]

    if link.startswith("#"):
        return None

    description = get_text(list_item)
    return ExtractInfo(name, link, description, None)


def flat(ast):
    queue = ast.copy()
    while queue:
        item = queue.pop()

        if "children" in item and type(item["children"]) is list:
            queue = queue + item["children"]

        yield item


def find_type_single(ast, type):
    def is_type(token):
        return token["type"] == type

    try:
        return next(filter(is_type, flat(ast)))
    except StopIteration:
        return None


def get_children(token):
    if "children" in token:
        return token["children"]
    else:
        return []


def get_text(ast):
    return " ".join([token["text"] for token in flat(ast) if "text" in token])
