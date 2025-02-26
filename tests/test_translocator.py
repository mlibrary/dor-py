import pytest

from pathlib import Path

from dor.providers.file_system_file_provider import FilesystemFileProvider
from dor.providers.minter_provider import MinterProvider
from dor.providers.translocator import Translocator


class TestMinterProvider(MinterProvider):

    def mint(self) -> str:
        return "a2574fa4-f169-48b5-a5df-6287fe5ef1aa"

@pytest.fixture
def workspaces_path() -> Path:
    return Path("tests/test_workspaces")

@pytest.fixture
def inbox_path() -> Path:
    return Path("tests/fixtures/test_inbox")

def test_create_translocator(inbox_path: Path, workspaces_path: Path) -> None:
    Translocator(
        inbox_path=inbox_path, workspaces_path=workspaces_path, minter_provider=TestMinterProvider(), file_provider=FilesystemFileProvider()
    )
    
def test_translocator_can_create_workspace(inbox_path: Path, workspaces_path: Path) -> None:
    file_provider = FilesystemFileProvider()
    minter_provider = TestMinterProvider()
    file_provider.delete_dir_and_contents(
        Path(workspaces_path / minter_provider.mint())
    )
    translocator = Translocator(
        inbox_path=inbox_path,
        workspaces_path=workspaces_path,
        minter_provider=minter_provider,
        file_provider=file_provider
    )
    workspace = translocator.create_workspace_for_package("xyzzy-0001-v1")

    assert workspace.identifier == str(workspaces_path / minter_provider.mint())
    assert Path(workspace.identifier).exists()
