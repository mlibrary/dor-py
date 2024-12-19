from pathlib import Path

import pytest

from dor.adapters.bag_reader import BagReader, DorInfoMissingError, ValidationError


@pytest.fixture
def valid_bag_path() -> Path:
    return Path("tests/fixtures/test_bag_valid")

@pytest.fixture
def dor_info_missing_bag_path() -> Path:
    return Path("tests/fixtures/test_bag_missing_dor_info")

def test_passes_validation(valid_bag_path: Path):
    reader = BagReader(valid_bag_path)
    reader.validate()

def test_fails_validation_when_dor_info_missing(dor_info_missing_bag_path: Path):
    reader = BagReader(dor_info_missing_bag_path)
    with pytest.raises(ValidationError) as excinfo:
        reader.validate()
    expected_message = (
        "Validation failed with the following message: " +
        "\"Bag is incomplete: dor-info.txt exists in manifest but was not found on filesystem\""
    )
    assert expected_message == excinfo.value.message

def test_fails_validation_when_file_has_been_modified():
    path = Path("tests/fixtures/test_bag_with_modified_file")
    reader = BagReader(path)
    with pytest.raises(ValidationError) as excinfo:
        reader.validate()
    expected_message = (
        "Validation failed with the following message: " +
        "\"Payload-Oxum validation failed. Expected 1 files and 13 bytes but found 1 files and 15 bytes\""
    )
    assert expected_message == excinfo.value.message

def test_fails_validation_when_dor_info_not_in_tagmanifest():
    path = Path("tests/fixtures/test_bag_with_dor_info_not_in_manifest")
    reader = BagReader(path)
    with pytest.raises(ValidationError) as excinfo:
        reader.validate()
    expected_message = "dor-info.txt must be listed in the tagmanifest file."
    assert expected_message == excinfo.value.message

def test_read_dor_info(valid_bag_path: Path):
    reader = BagReader(valid_bag_path)
    assert reader.dor_info == {"Deposit-Group-Identifier": "d752b492-eb0b-4150-bcf5-b4cb74bd4a7f"}

def test_read_dor_info_when_missing(dor_info_missing_bag_path: Path):
    reader = BagReader(dor_info_missing_bag_path)
    with pytest.raises(DorInfoMissingError):
        reader.dor_info

