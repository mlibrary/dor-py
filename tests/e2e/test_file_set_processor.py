import pytest


# 00001.tif
# 00001.txt
#
# -> { "0001": [ "0001.tif", "0001.txt" ] }
#
# op = { "0001.tif": "basic-image", "0001.txt": "append-service" }
#
# POST /upload?name=0001&files=[]&config=
#
# {
# 	"image/*": ["CompressSourceImage"],
# 	"text/*": [
# 		"AppendUses", {
# 			"target": {
# 				"function": ["function:source"],
# 				"format": "format:text-plain"
# 			},
# 			"uses": [ "function:service" ]
# 		}
# 	]
# }


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
        "profile": "basic-image"
        # "profile": { "test_image.jpg": "basic-image" },
    }
    response = test_client.post("api/v1/filesets", files=upload_files, data=data)

    assert response.status_code == 200
