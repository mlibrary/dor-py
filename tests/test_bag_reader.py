from pathlib import Path

import pytest

from dor.adapters.bag_reader import BagReader, DorInfoMissingError

@pytest.fixture
def valid_bag_path() -> Path:
    return Path("tests/fixtures/test_bag_valid")

@pytest.fixture
def dor_info_missing_bag_path() -> Path:
    return Path("tests/fixtures/test_bag_missing_dor_info")

def test_is_valid(valid_bag_path: Path):
    reader = BagReader(valid_bag_path)
    assert reader.is_valid()

def test_read_dor_info(valid_bag_path: Path):
    reader = BagReader(valid_bag_path)
    assert reader.dor_info == {"Deposit-Group-Identifier": "d752b492-eb0b-4150-bcf5-b4cb74bd4a7f"}

def test_dor_info_missing(dor_info_missing_bag_path: Path):
    reader = BagReader(dor_info_missing_bag_path)
    assert not reader.is_valid()

def test_read_dor_info_when_missing(dor_info_missing_bag_path: Path):
    reader = BagReader(dor_info_missing_bag_path)
    with pytest.raises(DorInfoMissingError):
        reader.dor_info

def test_is_not_valid_when_dor_info_not_in_tagmanifest():
    path = Path("tests/fixtures/test_bag_with_dor_info_not_in_manifest")
    reader = BagReader(path)
    assert not reader.is_valid()
