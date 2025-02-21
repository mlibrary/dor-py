from pathlib import Path
from typing import Callable

import pytest

from dor.adapters.bag_adapter import BagAdapter, DorInfoMissingError, ValidationError
from dor.providers.file_system_file_provider import FilesystemFileProvider


@pytest.fixture
def bag_adapter_instance() -> Callable[[Path], BagAdapter]:
    def _create_instance(path: Path) -> BagAdapter:
        return BagAdapter.load(path=path, file_provider=FilesystemFileProvider())
    return _create_instance


@pytest.fixture
def test_bags_path() -> Path:
    return Path("tests/fixtures/test_bags")


def test_passes_validation(
    test_bags_path: Path, bag_adapter_instance: Callable[[Path], BagAdapter]
):
    path = test_bags_path / "test_bag_valid"
    bag = bag_adapter_instance(path)
    bag.validate()


def test_fails_validation_when_dor_info_missing(
    test_bags_path: Path, bag_adapter_instance: Callable[[Path], BagAdapter]
):
    path = test_bags_path / "test_bag_missing_dor_info"
    bag = bag_adapter_instance(path)
    with pytest.raises(ValidationError) as excinfo:
        bag.validate()
    expected_message = (
        "Validation failed with the following message: " +
        "\"Bag is incomplete: dor-info.txt exists in manifest but was not found on filesystem\""
    )
    assert expected_message == excinfo.value.message


def test_fails_validation_when_file_has_been_modified(
    test_bags_path: Path, bag_adapter_instance: Callable[[Path], BagAdapter]
):
    path = test_bags_path / "test_bag_with_modified_file"
    bag = bag_adapter_instance(path)
    with pytest.raises(ValidationError) as excinfo:
        bag.validate()
    expected_message = (
        "Validation failed with the following message: " +
        "\"Payload-Oxum validation failed. Expected 1 files and 13 bytes but found 1 files and 15 bytes\""
    )
    assert expected_message == excinfo.value.message


def test_fails_validation_when_dor_info_not_in_tagmanifest(
    test_bags_path: Path, bag_adapter_instance: Callable[[Path], BagAdapter]
):
    path = test_bags_path / "test_bag_with_dor_info_not_in_manifest"
    bag = bag_adapter_instance(path)
    with pytest.raises(ValidationError) as excinfo:
        bag.validate()
    expected_message = "dor-info.txt must be listed in the tagmanifest file."
    assert expected_message == excinfo.value.message


def test_read_dor_info(
    test_bags_path: Path, bag_adapter_instance: Callable[[Path], BagAdapter]
):
    path = test_bags_path / "test_bag_valid"
    bag = bag_adapter_instance(path)
    assert bag.dor_info == {"Deposit-Group-Identifier": "d752b492-eb0b-4150-bcf5-b4cb74bd4a7f"}


def test_read_dor_info_when_missing(
    test_bags_path: Path, bag_adapter_instance: Callable[[Path], BagAdapter]
):
    path = test_bags_path / "test_bag_missing_dor_info"
    bag = bag_adapter_instance(path)
    with pytest.raises(DorInfoMissingError):
        bag.dor_info


@pytest.fixture
def payload_path():
    payload_path = Path("tests/test_payload")
    file_provider = FilesystemFileProvider()
    file_provider.delete_dir_and_contents(payload_path)
    file_provider.create_directory(payload_path)
    with open(payload_path / "hello.txt", "w") as file:
        file.write("Hello World!\n")
    return payload_path


def test_adapter_can_make_bag(payload_path):
    file_provider = FilesystemFileProvider()
    dor_info = {"Action": "Store"}
    bag = BagAdapter.make(payload_path, dor_info, file_provider)
    bag.validate()
