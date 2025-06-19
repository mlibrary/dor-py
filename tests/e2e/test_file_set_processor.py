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
    fileset_helper = FileSetIdentifier(project_id="collid", file_name="test_image.jpg")
    fileset_path = Path(f"{config.filesets_path}/{fileset_helper.identifier}")
    file_provider = FilesystemFileProvider()
    file_provider.delete_dir_and_contents(path=fileset_path)
    file_path = f"tests/fixtures/test_file_set_processor/{fileset_helper.file_name}"
    upload_files = []
    upload_files.append(
        (
            "files",
            (
                fileset_helper.file_name,
                open(file_path, "rb"),
                "image/jpeg",
            ),
        )
    )
    data = {
        "name": fileset_helper.basename,
        "project_id": fileset_helper.project_id,
        "file_profiles": json.dumps({
            f"{fileset_helper.file_name}": ["compress-source"]
        })
    }
    response = test_client.post("api/v1/filesets", files=upload_files, data=data)

    assert response.status_code == 200
    assert fileset_path.exists()


@pytest.mark.usefixtures("test_client")
def test_filesets_api_returns_200_and_summary_for_image_with_ocr(
    test_client
) -> None:
    fileset_helper = FileSetIdentifier(project_id="collid", file_name="quick-brown.tiff")
    fileset_path = Path(f"{config.filesets_path}/{fileset_helper.identifier}")
    file_provider = FilesystemFileProvider()
    file_provider.delete_dir_and_contents(path=fileset_path)
    file_path = f"tests/fixtures/test_file_set_processor_with_ocr/{fileset_helper.file_name}"
    upload_files = []
    upload_files.append(
        (
            "files",
            (
                fileset_helper.file_name,
                open(file_path, "rb"),
                "image/tiff",
            ),
        )
    )
    data = {
        "name": fileset_helper.basename,
        "project_id": fileset_helper.project_id,
        "file_profiles": json.dumps({
            f"{fileset_helper.file_name}": ["compress-source", "extract-text"]
        })
    }

    response = test_client.post("api/v1/filesets", files=upload_files, data=data)

    assert response.status_code == 200
    assert fileset_path.exists()
