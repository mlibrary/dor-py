import json

import pytest


@pytest.mark.usefixtures("test_client")
def test_filesets_api_returns_200_and_summary(
    test_client
) -> None:
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
        "project_id": "today",
        "file_profiles": json.dumps({
            "test_image.jpg": ["compress-source"]
        })
    }
    response = test_client.post("api/v1/filesets", files=upload_files, data=data)

    assert response.status_code == 200


@pytest.mark.usefixtures("test_client")
def test_filesets_api_returns_200_and_summary_for_image_with_ocr(
    test_client
) -> None:
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
        "project_id": "today",
        "file_profiles": json.dumps({
            "quick-brown.tiff": ["compress-source", "extract-text"]
        })
    }

    response = test_client.post("api/v1/filesets", files=upload_files, data=data)

    assert response.status_code == 200
