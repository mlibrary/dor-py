import json
from datetime import datetime, UTC
from pathlib import Path

import pytest

from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.package_generator import DepositGroup, PackageGenerator, PackageResult


@pytest.fixture
def fixtures_path() -> Path:
    return Path("tests/fixtures/test_package_generator")


@pytest.fixture
def test_output_path() -> Path:
    file_provider = FilesystemFileProvider()
    test_output_path = Path("tests/test_package_generator")
    file_provider.delete_dir_and_contents(test_output_path)
    file_provider.create_directory(test_output_path)
    return test_output_path


@pytest.fixture
def deposit_group() -> DepositGroup:
    return DepositGroup(
        identifier="23312082-44d8-489e-97f4-383329de9ac5",
        date=datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)
    )


def test_generator_generates_package(
    fixtures_path: Path, test_output_path: Path, deposit_group: DepositGroup
) -> None:
    metadata_path = fixtures_path / "sample_package_metadata.json"
    metadata = json.loads(metadata_path.read_text())

    generator = PackageGenerator(
        file_provider=FilesystemFileProvider(),
        metadata=metadata,
        deposit_group=deposit_group,
        output_path=test_output_path,
        file_set_path=fixtures_path / "file_sets",
        timestamp=datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)
    )
    result = generator.generate()

    root_identifier = "00000000-0000-0000-0000-000000000001"
    package_identifier = f"{root_identifier}_19700101000000"
    package_data_path = test_output_path / package_identifier / "data"

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
        deposit_group_identifier=deposit_group.identifier,
        success=True,
        message="Generated package successfully!"
    )


def test_generator_fails_when_metadata_references_missing_file_set(
    fixtures_path: Path, test_output_path: Path, deposit_group: DepositGroup
) -> None:
    metadata_path = fixtures_path / "sample_package_metadata_with_missing_file_set.json"
    metadata = json.loads(metadata_path.read_text())

    generator = PackageGenerator(
        file_provider=FilesystemFileProvider(),
        metadata=metadata,
        deposit_group=deposit_group,
        output_path=test_output_path,
        file_set_path=fixtures_path / "file_sets",
        timestamp=datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)
    )
    result = generator.generate()

    package_identifier = "00000000-0000-0000-0000-000000000001_19700101000000"
    assert not (test_output_path / package_identifier).exists()
    assert result == PackageResult(
        package_identifier=package_identifier,
        deposit_group_identifier=deposit_group.identifier,
        success=False,
        message="The following file sets were not found: 00000000-0000-0000-0000-000000001003"
    )


def test_generator_fails_when_metadata_is_missing_file_data(
    fixtures_path: Path, test_output_path: Path, deposit_group: DepositGroup
) -> None:
    metadata_path = fixtures_path / "sample_package_metadata_without_file_data.json"
    metadata = json.loads(metadata_path.read_text())

    generator = PackageGenerator(
        file_provider=FilesystemFileProvider(),
        metadata=metadata,
        deposit_group=deposit_group,
        output_path=test_output_path,
        file_set_path=Path("tests/fixtures/test_package_generator/file_sets"),
        timestamp=datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)
    )
    result = generator.generate()

    package_identifier = "00000000-0000-0000-0000-000000000001_19700101000000"
    assert not (test_output_path / package_identifier).exists()
    assert result == PackageResult(
        package_identifier=package_identifier,
        deposit_group_identifier=deposit_group.identifier,
        success=False,
        message=(
            "Expected to find a single instance of metadata file data for use \"PROVENANCE\" " +
            "but found 0"
        )
    )


def test_generator_fails_when_metadata_is_missing_struct_map(
    fixtures_path: Path, test_output_path: Path, deposit_group: DepositGroup
) -> None:
    metadata_path = fixtures_path / "sample_package_metadata_without_struct_map.json"
    metadata = json.loads(metadata_path.read_text())

    generator = PackageGenerator(
        file_provider=FilesystemFileProvider(),
        metadata=metadata,
        deposit_group=deposit_group,
        output_path=test_output_path,
        file_set_path=fixtures_path / "file_sets",
        timestamp=datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)
    )
    result = generator.generate()

    package_identifier = "00000000-0000-0000-0000-000000000001_19700101000000"
    assert not (test_output_path / package_identifier).exists()
    assert result == PackageResult(
        package_identifier=package_identifier,
        deposit_group_identifier=deposit_group.identifier,
        success=False,
        message="Expected to find a single \"PHYSICAL\" structure object but found 0"
    )
