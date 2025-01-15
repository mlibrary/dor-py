from pathlib import Path
import pytest

from dor.providers.file_system_file_provider import FilesystemHandler


file_provider = FilesystemHandler()


@pytest.mark.parametrize(
    "base_path, path_to_apply, expected_path",
    [
        (
            Path("/tmp/UID-00001/data/00000000-0000-0000-0000-000000000001/descriptor"),
            "../metadata/images/pic.jpg",
            Path(
                "/tmp/UID-00001/data/00000000-0000-0000-0000-000000000001/metadata/images/pic.jpg"
            ),
        ),
        (
            Path("/tmp/UID-00001/data/00000000-0000-0000-0000-000000000001/descriptor"),
            ".",
            Path("/tmp/UID-00001/data/00000000-0000-0000-0000-000000000001/descriptor"),
        ),
        (
            Path("/tmp/UID-00001/data/00000000-0000-0000-0000-000000000001/descriptor"),
            "data/00001.txt",
            Path(
                "/tmp/UID-00001/data/00000000-0000-0000-0000-000000000001/descriptor/data/00001.txt"
            ),
        ),
        (
            Path("/tmp/UID-00001/data/00000000-0000-0000-0000-000000000001/descriptor"),
            "../",
            Path("/tmp/UID-00001/data/00000000-0000-0000-0000-000000000001"),
        ),
    ],
)
def test_apply_relative_path(base_path, path_to_apply, expected_path):
    result = file_provider.apply_relative_path(base_path, path_to_apply)
    assert result == expected_path


@pytest.mark.parametrize(
    "file_path, expected_dir",
    [
        (
            Path(
                "/tmp/UID-00001/data/00000000-0000-0000-0000-000000000001/metadata/images/pic.jpg"
            ),
            Path(
                "/tmp/UID-00001/data/00000000-0000-0000-0000-000000000001/metadata/images"
            ),
        ),
        (Path("/file.txt"), Path("/")),
        (Path("file.txt"), Path(".")),
        (Path(""), Path(".")),
    ],
)
def test_get_data_dir(file_path, expected_dir):
    result = file_provider.get_data_dir(file_path)
    assert result == expected_dir
