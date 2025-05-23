from pathlib import Path

import pytest

from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.translocator import Translocator


@pytest.fixture
def workspaces_path() -> Path:
    return Path("tests/output/test_workspaces")


@pytest.fixture
def inbox_path() -> Path:
    return Path("tests/fixtures/test_inbox")


def test_create_translocator(inbox_path: Path, workspaces_path: Path) -> None:
    Translocator(
        inbox_path=inbox_path, workspaces_path=workspaces_path, minter=lambda: "some_id", file_provider=FilesystemFileProvider()
    )


def test_translocator_can_create_workspace(inbox_path: Path, workspaces_path: Path) -> None:
    file_provider = FilesystemFileProvider()
    file_provider.delete_dir_and_contents(
        Path(workspaces_path / "some_id")
    )
    translocator = Translocator(
        inbox_path=inbox_path,
        workspaces_path=workspaces_path,
        minter=lambda: "some_id",
        file_provider=file_provider
    )
    workspace = translocator.create_workspace_for_package("xyzzy-00000000-0000-0000-0000-000000000001-v1")

    assert workspace.identifier == str(workspaces_path / "some_id")
    assert Path(workspace.identifier).exists()
