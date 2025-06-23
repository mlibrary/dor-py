import json
from pathlib import Path

import pytest

from dor.config import config
from dor.providers.file_set_identifier import FileSetIdentifier
from dor.providers.file_system_file_provider import FilesystemFileProvider


@pytest.mark.usefixtures("test_client")
def test_filesets_api_returns_200_and_summary(
    test_client
) -> None:
    file_provider = FilesystemFileProvider()
    file_provider.delete_dir_and_contents(path=Path(f"{config.filesets_path}/c6d9deda-03b9-a701-1613-6fedac69d6ba"))
    file_path = "tests/fixtures/test_file_set_processor/test_image.jpg"
    upload_files = []
    upload_files.append(
        (
            "files",
            (
                "test_image.jpg",
                open(file_path, "rb"),
                "image/jpeg",
            ),
        )
    )
    data = {
        "name": "test_image",
        "project_id": "collid",
        "file_profiles": json.dumps({
            "test_image.jpg": ["compress-source"]
        })
    }
    response = test_client.post("api/v1/filesets", files=upload_files, data=data)

    assert response.status_code == 200
    assert Path(f"{config.filesets_path}/c6d9deda-03b9-a701-1613-6fedac69d6ba").exists()


@pytest.mark.usefixtures("test_client")
def test_filesets_api_returns_200_and_summary_for_image_with_ocr(
    test_client
) -> None:
    file_provider = FilesystemFileProvider()
    file_provider.delete_dir_and_contents(path=Path(f"{config.filesets_path}/faae8c28-642f-e921-15ed-9fa8669354df"))
    file_path = "tests/fixtures/test_file_set_processor_with_ocr/quick-brown.tiff"
    upload_files = []
    upload_files.append(
        (
            "files",
            (
                "quick-brown.tiff",
                open(file_path, "rb"),
                "image/tiff",
            ),
        )
    )
    data = {
        "name": "quick-brown",
        "project_id": "collid",
        "file_profiles": json.dumps({
            "quick-brown.tiff": ["compress-source", "extract-text"]
        })
    }

    response = test_client.post("api/v1/filesets", files=upload_files, data=data)

    assert response.status_code == 200
    assert Path(f"{config.filesets_path}/faae8c28-642f-e921-15ed-9fa8669354df").exists()
