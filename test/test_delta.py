import pytest

from awesome_crawler.delta import delta
from awesome_crawler.serialize import Output, OutputItem, OutputList, serialize


@pytest.fixture
def empty():
    return Output(lists=[])


@pytest.fixture
def old_output_3_items():
    items = [OutputItem(f"ITEM{i}", f"http://item{i}.com", "", "") for i in range(3)]
    list = OutputList("LIST1", "", "", items)
    return Output(lists=[list])


@pytest.fixture
def new_output_4_items():
    items = [OutputItem(f"ITEM{i}", f"http://item{i}.com", "", "") for i in range(4)]
    list = OutputList("LIST1", "", "", items)
    return Output(lists=[list])


def test_old_with_nothing_should_be_old(old_output_3_items, empty):
    delta_output = delta(serialize(empty), serialize(old_output_3_items))

    assert delta_output == old_output_3_items


def test_old_with_fourth_item_should_be_added(old_output_3_items, new_output_4_items):
    delta_output = delta(serialize(new_output_4_items), serialize(old_output_3_items))

    assert len(delta_output.lists[0].items) == 4
