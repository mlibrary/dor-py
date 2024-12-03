from pathlib import Path

from dor.adapters.bag_reader import BagReader


def test_is_valid():
    path = Path("tests/fixtures/test_bag_it")
    reader = BagReader(path)
    assert reader.is_valid()

def test_read_tag_file():
    path = Path("tests/fixtures/test_bag_it")
    reader = BagReader(path)
    assert reader.dor_info == {"deposit_group_identifier": "d752b492-eb0b-4150-bcf5-b4cb74bd4a7f"}
