import os
import shutil
from pathlib import Path
from typing import Any, Callable
import pytest

from dor.providers.file_system_file_provider import FilesystemFileProvider


file_provider = FilesystemFileProvider()


@pytest.mark.parametrize(
    "base_path, path_to_apply, expected_path",
    [
        (
            Path("/tmp/UID-00001/data/00000000-0000-0000-0000-000000000001/descriptor"),
            "../metadata/images/pic.jpg",
            Path("metadata/images/pic.jpg"),
        ),
        (
            Path("/tmp/UID-00001/data/00000000-0000-0000-0000-000000000001/descriptor"),
            ".",
            Path("descriptor"),
        ),
        (
            Path("/tmp/UID-00001/data/00000000-0000-0000-0000-000000000001/descriptor"),
            "data/00001.txt",
            Path("descriptor/data/00001.txt"),
        ),
        (
            Path("/tmp/UID-00001/data/00000000-0000-0000-0000-000000000001/descriptor"),
            "../",
            Path(""),
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
def test_get_descriptor_dir(file_path, expected_dir):
    result = file_provider.get_descriptor_dir(file_path)
    assert result == expected_dir

@pytest.mark.parametrize(
    "base_path, path_to_apply, expected_result",
    [
        (
            Path("/test/base/path"),
            "test/path/to/apply",
            Path("/test/base/path/test/path/to/apply"),
        )
    ],
)
def test_get_norm_path(base_path, path_to_apply, expected_result):
    assert file_provider.get_norm_path(base_path, path_to_apply) == expected_result


@pytest.mark.parametrize(
    "base_path, path_to_apply, expected_result",
    [
        (
            Path("/test/base/path"),
            "test/path/to/apply",
            Path("/test/base/path/test/path/to/apply"),
        )
    ],
)
def test_get_combined_path(base_path, path_to_apply, expected_result):
    assert file_provider.get_combined_path(base_path, path_to_apply) == expected_result


@pytest.fixture
def create_tmp_test_dir():
    tmp_path = Path("tests/test_dir")
    tmp_path.mkdir()  
    yield tmp_path

    # Teardown
    if tmp_path.exists():
        shutil.rmtree(tmp_path)


def test_delete_dir_and_contents(create_tmp_test_dir):
    tmp_path = create_tmp_test_dir

    test_file = tmp_path / "test_file.txt"
    test_file.write_text("Test file")

    file_provider.delete_dir_and_contents(tmp_path)
    assert not test_file.exists()


def test_clone_directory_structure(create_tmp_test_dir):
    tmp_path = create_tmp_test_dir
    source_path = tmp_path / Path("source")
    destination_path = tmp_path / Path("dest")
    source_path.mkdir()

    test_file = source_path / "file1.txt"
    test_file.write_text("Test file1")

    file_provider.clone_directory_structure(source_path, destination_path)
    assert (destination_path / "file1.txt").exists()


def test_create_directory(create_tmp_test_dir):
    tmp_path = create_tmp_test_dir
    new_dir = tmp_path / "new_dir"

    file_provider.create_directory(new_dir)
    assert new_dir.exists()


def test_create_directories(create_tmp_test_dir):
    tmp_path = create_tmp_test_dir
    new_dir = tmp_path / "new_dir" / "subdir"

    file_provider.create_directories(new_dir)
    assert new_dir.exists()
