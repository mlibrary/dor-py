import json
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

import pytest

from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.package_generator import PackageGenerator, PackageResult

@pytest.fixture
def sample_package_metadata() -> dict[str, Any]:
    metadata_path = Path("tests/fixtures/test_packager/sample_package_metadata.json")
    sample_package_metadata = json.loads(metadata_path.read_text())
    return sample_package_metadata


def test_generator_generates_package(sample_package_metadata) -> None:
    file_provider = FilesystemFileProvider()
    test_packager_path = Path("tests/test_packager")
    file_provider.delete_dir_and_contents(test_packager_path)
    file_provider.create_directory(test_packager_path)

    generator = PackageGenerator(
        file_provider=file_provider,
        metadata=sample_package_metadata,
        output_path=test_packager_path,
        file_set_path=Path("tests/fixtures/test_packager/file_sets"),
        timestamp=datetime(1970, 1, 1, 0, 0, 0, tzinfo=UTC)
    )
    result = generator.generate()

    # Metadata files were created
    root_identifier = "00000000-0000-0000-0000-000000000001"
    package_identifier = f"{root_identifier}_19700101000000"
    root_resource_metadata_path = test_packager_path / package_identifier / root_identifier / "metadata"
    assert (root_resource_metadata_path / f"{root_identifier}.common.json").exists()
    assert (root_resource_metadata_path / f"{root_identifier}.metadata.json").exists()
    assert (root_resource_metadata_path / f"{root_identifier}.premis.object.xml").exists()

    # File sets were incorporated
    file_set_one_path = test_packager_path / package_identifier / "00000000-0000-0000-0000-000000001001"
    assert file_set_one_path.exists()
    file_set_two_path = test_packager_path / package_identifier / "00000000-0000-0000-0000-000000001002"
    assert file_set_two_path.exists()

    # Package result returned
    assert result == PackageResult(
        package_identifier=package_identifier,
        success=True,
        message="Generated package successfully!"
    )

