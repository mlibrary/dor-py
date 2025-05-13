import pytest

@pytest.mark.usefixtures("test_client")
def test_filesets_api_returns_200_and_summary(
    test_client
) -> None:
    file_path = "/app/tests/fixtures/test_basic_copy/test_image.jpg"
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
        "profile": "basic-image",
    }
    response = test_client.post("api/v1/filesets", files=upload_files, data=data)

    assert response.status_code == 200
