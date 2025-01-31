from pathlib import Path
from typing import Callable

from dor.providers.file_system_file_provider import FilesystemFileProvider
import pytest

from dor.adapters.bag_adapter import BagAdapter, DorInfoMissingError, ValidationError


@pytest.fixture
def bag_adapter_instance() -> Callable[[Path], BagAdapter]:
    def _create_instance(path: Path) -> BagAdapter:
        return BagAdapter(path=path, file_provider=FilesystemFileProvider())
    return _create_instance


@pytest.fixture
def test_bags_path() -> Path:
    return Path("tests/fixtures/test_bags")


def test_passes_validation(
    test_bags_path: Path, bag_adapter_instance: Callable[[Path], BagAdapter]):
    path = test_bags_path / "test_bag_valid"
    reader = bag_adapter_instance(path)
    reader.validate()


def test_fails_validation_when_dor_info_missing(
    test_bags_path: Path, bag_adapter_instance: Callable[[Path], BagAdapter]):
    path = test_bags_path / "test_bag_missing_dor_info"
    reader = bag_adapter_instance(path)
    with pytest.raises(ValidationError) as excinfo:
        reader.validate()
    expected_message = (
        "Validation failed with the following message: " +
        "\"Bag is incomplete: dor-info.txt exists in manifest but was not found on filesystem\""
    )
    assert expected_message == excinfo.value.message


def test_fails_validation_when_file_has_been_modified(
    test_bags_path: Path, bag_adapter_instance: Callable[[Path], BagAdapter]):
    path = test_bags_path / "test_bag_with_modified_file"
    reader = bag_adapter_instance(path)
    with pytest.raises(ValidationError) as excinfo:
        reader.validate()
    expected_message = (
        "Validation failed with the following message: " +
        "\"Payload-Oxum validation failed. Expected 1 files and 13 bytes but found 1 files and 15 bytes\""
    )
    assert expected_message == excinfo.value.message


def test_fails_validation_when_dor_info_not_in_tagmanifest(
    test_bags_path: Path, bag_adapter_instance: Callable[[Path], BagAdapter]):
    path = test_bags_path / "test_bag_with_dor_info_not_in_manifest"
    reader = bag_adapter_instance(path)
    with pytest.raises(ValidationError) as excinfo:
        reader.validate()
    expected_message = "dor-info.txt must be listed in the tagmanifest file."
    assert expected_message == excinfo.value.message


def test_read_dor_info(
    test_bags_path: Path, bag_adapter_instance: Callable[[Path], BagAdapter]):
    path = test_bags_path / "test_bag_valid"
    reader = bag_adapter_instance(path)
    assert reader.dor_info == {"Deposit-Group-Identifier": "d752b492-eb0b-4150-bcf5-b4cb74bd4a7f"}


def test_read_dor_info_when_missing(
    test_bags_path: Path, bag_adapter_instance: Callable[[Path], BagAdapter]):
    path = test_bags_path / "test_bag_missing_dor_info"
    reader = bag_adapter_instance(path)
    with pytest.raises(DorInfoMissingError):
        reader.dor_info
