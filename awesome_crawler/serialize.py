import dataclasses
import json

from cattr import structure, unstructure


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


def serialize(output: Output) -> str:
    return json.dumps(unstructure(output))


def deserialize(data: str) -> Output:
    return structure(json.loads(data), Output)
