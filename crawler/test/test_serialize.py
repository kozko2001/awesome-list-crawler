import json

import pytest

from awesome_crawler.serialize import (
    Output,
    OutputItem,
    OutputList,
    deserialize,
    serialize,
)


@pytest.fixture
def output():
    items = [OutputItem(f"ITEM{i}", f"http://item{i}.com", "", "") for i in range(3)]
    list = OutputList("LIST1", "", "", items)
    return Output(lists=[list])


def test_serialize(output):
    s = serialize(output)
    d = json.loads(s)
    assert len(d["lists"][0]["items"]) == 3


def test_unserialize(output):
    s = serialize(output)
    o = deserialize(s)

    assert o == output
