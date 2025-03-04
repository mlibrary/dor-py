import pytest

from pathlib import Path

from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.translocator import Translocator

from utils.minter import minter

@pytest.fixture
def workspaces_path() -> Path:
    return Path("tests/test_workspaces")

@pytest.fixture
def inbox_path() -> Path:
    return Path("tests/fixtures/test_inbox")

def test_create_translocator(inbox_path: Path, workspaces_path: Path) -> None:
    Translocator(
        inbox_path=inbox_path, workspaces_path=workspaces_path, minter=minter, file_provider=FilesystemFileProvider()
    )
    
def test_translocator_can_create_workspace(inbox_path: Path, workspaces_path: Path) -> None:
    mint = 'a2574fa4-f169-48b5-a5df-6287fe5ef1aa'
    file_provider = FilesystemFileProvider()
    file_provider.delete_dir_and_contents(
        Path(workspaces_path / mint)
    )
    translocator = Translocator(
        inbox_path=inbox_path,
        workspaces_path=workspaces_path,
        minter=lambda : mint,
        file_provider=file_provider
    )
    workspace = translocator.create_workspace_for_package("xyzzy-0001-v1")

    assert workspace.identifier == str(workspaces_path / mint)
    assert Path(workspace.identifier).exists()
