import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

import pytest

from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.package_generator import DepositGroup, PackageGenerator, PackageResult


@pytest.fixture
def sample_package_metadata() -> dict[str, Any]:
    metadata_path = Path("tests/fixtures/test_packager/sample_package_metadata.json")
    sample_package_metadata = json.loads(metadata_path.read_text())
    return sample_package_metadata


@pytest.fixture
def sample_package_metadata_with_missing_file_set() -> dict[str, Any]:
    metadata_path = Path("tests/fixtures/test_packager/sample_package_metadata_with_missing_file_set.json")
    sample_package_metadata_with_missing_file_set = json.loads(metadata_path.read_text())
    return sample_package_metadata_with_missing_file_set


def test_generator_generates_package(sample_package_metadata) -> None:
    file_provider = FilesystemFileProvider()
    test_path = Path("tests/test_package_generator")
    file_provider.delete_dir_and_contents(test_path)
    file_provider.create_directory(test_path)

    generator = PackageGenerator(
        file_provider=file_provider,
        metadata=sample_package_metadata,
        deposit_group=DepositGroup(
            identifier="23312082-44d8-489e-97f4-383329de9ac5",
            date=datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)
        ),
        output_path=test_path,
        file_set_path=Path("tests/fixtures/test_packager/file_sets"),
        timestamp=datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)
    )
    result = generator.generate()

    root_identifier = "00000000-0000-0000-0000-000000000001"
    package_identifier = f"{root_identifier}_19700101000000"
    package_data_path = test_path / package_identifier / "data"

    # Metadata files were created
    root_resource_metadata_path = package_data_path / root_identifier / "metadata"
    assert (root_resource_metadata_path / f"{root_identifier}.common.json").exists()
    assert (root_resource_metadata_path / f"{root_identifier}.metadata.json").exists()
    assert (root_resource_metadata_path / f"{root_identifier}.premis.object.xml").exists()

    # File sets were incorporated
    file_set_one_path = package_data_path / "00000000-0000-0000-0000-000000001001"
    assert file_set_one_path.exists()
    file_set_two_path = package_data_path / "00000000-0000-0000-0000-000000001002"
    assert file_set_two_path.exists()

    # Descriptor file was created
    descriptor_path = package_data_path / root_identifier / "descriptor"
    descriptor_file = f"{root_identifier}.monograph.mets2.xml"
    assert (descriptor_path / descriptor_file).exists()

    # Package result returned
    assert result == PackageResult(
        package_identifier=package_identifier,
        success=True,
        message="Generated package successfully!"
    )


def test_generator_fails_when_missing_file_sets(sample_package_metadata_with_missing_file_set) -> None:
    file_provider = FilesystemFileProvider()
    test_path = Path("tests/test_package_generator")
    file_provider.delete_dir_and_contents(test_path)
    file_provider.create_directory(test_path)

    generator = PackageGenerator(
        file_provider=file_provider,
        metadata=sample_package_metadata_with_missing_file_set,
        deposit_group=DepositGroup(
            identifier="23312082-44d8-489e-97f4-383329de9ac5",
            date=datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)
        ),
        output_path=test_path,
        file_set_path=Path("tests/fixtures/test_packager/file_sets"),
        timestamp=datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)
    )
    result = generator.generate()

    assert result == PackageResult(
        package_identifier="00000000-0000-0000-0000-000000000001_19700101000000",
        success=False,
        message="The following file sets were not found: 00000000-0000-0000-0000-000000001003"
    )
